/* ============================================================
   otter-hub · core.js v1.0
   统一认证 + Gist 同步引擎
   所有应用共用这一份
   ============================================================ */

// ── 常量 ──────────────────────────────────────────────────
const GIST_FILENAME = 'otter-unified.json';
const GIST_DESC     = '海獭全家桶 · 数据同步';
const STORAGE_KEYS = {
  TOKEN:   'otter_unified_token',
  GIST_ID: 'otter_unified_gist_id',
  USER:    'otter_unified_user',
  DATA:    'otter_unified_data',   // 本地缓存副本
  META:    'otter_unified_meta',   // { lastSync, version }
};

// ── 默认数据结构 ─────────────────────────────────────────
const DEFAULT_DATA = {
  version: '2.0.0',
  lastUpdated: 0,
  todo: {
    lists: [
      { id: 'list-default', name: '默认清单', color: '#FF6B5B', order: 0, emoji: '📋' }
    ],
    tasks: [],
    deleted: { lists: [], tasks: [] }
  },
  habits: {
    habits: [],
    checkins: {}
  },
  ledger: {
    records: [],
    categories: {
      income:  ['💰 工资', '🎁 奖金', '💵 兼职', '📦 退款'],
      expense: ['🍜 餐饮', '🚇 交通', '🏠 住房', '🎮 娱乐', '🛒 购物', '💊 医疗', '📱 通讯', '📚 学习']
    },
    budget: {}
  },
  homepage: {
    shortcuts: [
      { id: 'sh-github', name: 'GitHub', url: 'https://github.com', emoji: '🐙', color: '#98D8AA' },
      { id: 'sh-notion', name: 'Notion', url: 'https://notion.so', emoji: '📝', color: '#5BC4CF' }
    ],
    bgUrl: ''
  }
};

// ── 全局状态 ─────────────────────────────────────────────
let state = {
  token:   null,
  gistId:  null,
  user:    null,
  data:    null,
  isSyncing: false,
  listeners: [],
  offlineQueue: []
};

// ── 工具函数 ─────────────────────────────────────────────
function $id(id) { return document.getElementById(id); }

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

function isOnline() { return navigator.onLine; }

function now() { return Date.now(); }

// 深度合并两个对象（用于增量更新）
function deepMerge(base, updates) {
  const out = JSON.parse(JSON.stringify(base));
  for (const key in updates) {
    if (updates[key] && typeof updates[key] === 'object' && !Array.isArray(updates[key])) {
      out[key] = deepMerge(out[key] || {}, updates[key]);
    } else {
      out[key] = updates[key];
    }
  }
  return out;
}

// ── GitHub API ────────────────────────────────────────────
async function ghFetch(path, options = {}) {
  const res = await fetch(`https://api.github.com${path}`, {
    ...options,
    headers: {
      'Authorization': `token ${state.token}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── 核心 API ─────────────────────────────────────────────

// 初始化：从 localStorage 恢复状态
async function init() {
  state.token  = localStorage.getItem(STORAGE_KEYS.TOKEN);
  state.gistId = localStorage.getItem(STORAGE_KEYS.GIST_ID);
  const rawUser = localStorage.getItem(STORAGE_KEYS.USER);
  if (rawUser) {
    try { state.user = JSON.parse(rawUser); } catch {}
  }

  // 恢复本地缓存数据
  const rawData = localStorage.getItem(STORAGE_KEYS.DATA);
  if (rawData) {
    try { state.data = JSON.parse(rawData); } catch {}
  }

  // 如果有 token，验证并同步
  if (state.token) {
    try {
      await verifyToken();
      await pull();
    } catch (e) {
      console.warn('[core] 初始化同步失败', e.message);
      // token 无效，清除
      if (e.message.includes('401') || e.message.includes('Bad credentials')) {
        logout(true);
      }
    }
  }

  // 监听网络状态
  window.addEventListener('online',  () => { syncNow(); showToast('🌐 网络已恢复，正在同步', 'info'); });
  window.addEventListener('offline', () => { showToast('📴 已离线，数据暂存本地', 'warn'); });

  return !!state.token;
}

// 验证 Token
async function verifyToken() {
  const user = await ghFetch('/user');
  state.user = { login: user.login, name: user.name, avatar: user.avatar_url };
  localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(state.user));
  return user;
}

// 查找或创建 Gist
async function findOrCreateGist() {
  // 1. 尝试查找已有
  try {
    const gists = await ghFetch('/gists');
    const existing = gists.find(g =>
      g.description === GIST_DESC && g.files[GIST_FILENAME]
    );
    if (existing) {
      state.gistId = existing.id;
      localStorage.setItem(STORAGE_KEYS.GIST_ID, existing.id);
      return existing;
    }
  } catch (e) { console.warn('[core] 查找Gist失败', e); }

  // 2. 创建新 Gist
  const gist = await ghFetch('/gists', {
    method: 'POST',
    body: JSON.stringify({
      description: GIST_DESC,
      public: false,
      files: {
        [GIST_FILENAME]: {
          content: JSON.stringify(DEFAULT_DATA, null, 2)
        }
      }
    })
  });
  state.gistId = gist.id;
  localStorage.setItem(STORAGE_KEYS.GIST_ID, gist.id);
  state.data = JSON.parse(JSON.stringify(DEFAULT_DATA));
  persistData();
  return gist;
}

// 从 Gist 拉取
async function pull() {
  if (!state.token || !state.gistId) return;
  if (!isOnline()) return;

  try {
    const gist = await ghFetch(`/gists/${state.gistId}`);
    const file = gist.files[GIST_FILENAME];
    if (!file) return;

    const cloudData = JSON.parse(file.content);
    const localMeta = JSON.parse(localStorage.getItem(STORAGE_KEYS.META) || '{}');
    const cloudTime  = cloudData.lastUpdated || 0;
    const localTime  = localMeta.lastSync || 0;

    if (cloudTime > localTime) {
      // 云端更新，用云端
      state.data = cloudData;
      persistData();
      localStorage.setItem(STORAGE_KEYS.META, JSON.stringify({
        lastSync: now(),
        lastCloudUpdate: cloudTime
      }));
      notifyListeners('pull', cloudData);
    }
  } catch (e) {
    console.warn('[core] pull失败', e);
    throw e;
  }
}

// 推送到 Gist
async function push() {
  if (!state.token || !state.gistId || !isOnline()) return;

  state.isSyncing = true;
  notifySyncStatus('syncing');

  try {
    if (!state.data) state.data = getDefaultData();

    // 打时间戳
    state.data = { ...state.data, lastUpdated: now() };

    await ghFetch(`/gists/${state.gistId}`, {
      method: 'PATCH',
      body: JSON.stringify({
        description: GIST_DESC,
        files: {
          [GIST_FILENAME]: {
            content: JSON.stringify(state.data, null, 2)
          }
        }
      })
    });

    persistData();
    localStorage.setItem(STORAGE_KEYS.META, JSON.stringify({
      ...JSON.parse(localStorage.getItem(STORAGE_KEYS.META) || '{}'),
      lastSync: now()
    }));

    notifyListeners('push', state.data);
    notifySyncStatus('synced');
  } catch (e) {
    console.error('[core] push失败', e);
    notifySyncStatus('error');
    throw e;
  } finally {
    state.isSyncing = false;
  }
}

// 立即同步（拉+推）
async function syncNow() {
  if (!state.token || !isOnline()) return;
  try {
    await pull();
    await push();
  } catch (e) {
    console.warn('[core] syncNow失败', e.message);
  }
}

// 防抖同步（300ms）
let _syncTimer = null;
function scheduleSync() {
  if (_syncTimer) clearTimeout(_syncTimer);
  _syncTimer = setTimeout(() => syncNow(), 300);
}

// ── 登录 / 登出 ──────────────────────────────────────────

async function login(token) {
  if (!token || !token.trim()) throw new Error('Token 不能为空');

  state.token = token.trim();
  localStorage.setItem(STORAGE_KEYS.TOKEN, state.token);

  await verifyToken();
  await findOrCreateGist();
  await pull();

  notifyListeners('login', { user: state.user, data: state.data });
  showToast(`🦦 ${state.user.name || state.user.login}，欢迎回来！`, 'success');
  return state;
}

function logout(silent = false) {
  state.token  = null;
  state.gistId = null;
  state.user   = null;
  // 不清 data，清 localStorage 的 token/gist
  localStorage.removeItem(STORAGE_KEYS.TOKEN);
  localStorage.removeItem(STORAGE_KEYS.GIST_ID);
  localStorage.removeItem(STORAGE_KEYS.USER);

  notifyListeners('logout', {});
  if (!silent) showToast('已退出登录', 'info');
}

// ── 数据读写 ─────────────────────────────────────────────

function getData() {
  return state.data || JSON.parse(JSON.stringify(DEFAULT_DATA));
}

function setData(updates) {
  state.data = deepMerge(getData(), updates);
  persistData();
  scheduleSync();
  notifyListeners('change', state.data);
}

function persistData() {
  if (state.data) {
    localStorage.setItem(STORAGE_KEYS.DATA, JSON.stringify(state.data));
  }
}

function getDefaultData() {
  return JSON.parse(JSON.stringify(DEFAULT_DATA));
}

// ── Todo ─────────────────────────────────────────────────

function getTodo() {
  return getData().todo;
}

function addTask(listId, text, opts = {}) {
  const data = getData();
  const task = {
    id: uid(),
    listId: listId || data.todo.lists[0]?.id || 'list-default',
    text,
    completed: false,
    priority: opts.priority || 'normal',
    emoji: opts.emoji || '',
    createdAt: now(),
    completedAt: null,
    dueDate: opts.dueDate || null,
    tags: opts.tags || []
  };
  data.todo.tasks.unshift(task);
  setData({ todo: data.todo });
  return task;
}

function toggleTask(taskId) {
  const data = getData();
  const task = data.todo.tasks.find(t => t.id === taskId);
  if (!task) return;
  task.completed = !task.completed;
  task.completedAt = task.completed ? now() : null;
  setData({ todo: data.todo });
  return task;
}

function deleteTask(taskId) {
  const data = getData();
  data.todo.deleted.tasks.push(taskId);
  data.todo.tasks = data.todo.tasks.filter(t => t.id !== taskId);
  setData({ todo: data.todo });
}

function addList(name, emoji = '📋', color = '#FF6B5B') {
  const data = getData();
  const list = { id: uid(), name, emoji, color, order: data.todo.lists.length };
  data.todo.lists.push(list);
  setData({ todo: data.todo });
  return list;
}

function deleteList(listId) {
  const data = getData();
  if (data.todo.lists.length <= 1) return;
  data.todo.deleted.lists.push(listId);
  data.todo.lists = data.todo.lists.filter(l => l.id !== listId);
  // 把任务移到第一个清单
  data.todo.tasks.forEach(t => {
    if (t.listId === listId) t.listId = data.todo.lists[0].id;
  });
  setData({ todo: data.todo });
}

// ── Habits ───────────────────────────────────────────────

function getHabits() { return getData().habits; }

function addHabit(name, emoji = '✨', color = '#7EC8A3') {
  const data = getData();
  const habit = { id: uid(), name, emoji, color, createdAt: now() };
  data.habits.habits.push(habit);
  setData({ habits: data.habits });
  return habit;
}

function deleteHabit(habitId) {
  const data = getData();
  data.habits.habits = data.habits.habits.filter(h => h.id !== habitId);
  // 清除打卡记录
  for (const date in data.habits.checkins) {
    data.habits.checkins[date] = data.habits.checkins[date].filter(id => id !== habitId);
    if (data.habits.checkins[date].length === 0) delete data.habits.checkins[date];
  }
  setData({ habits: data.habits });
}

function toggleCheckin(habitId, dateStr = todayStr()) {
  const data = getData();
  if (!data.habits.checkins[dateStr]) data.habits.checkins[dateStr] = [];
  const idx = data.habits.checkins[dateStr].indexOf(habitId);
  if (idx >= 0) {
    data.habits.checkins[dateStr].splice(idx, 1);
  } else {
    data.habits.checkins[dateStr].push(habitId);
  }
  setData({ habits: data.habits });
  return data.habits.checkins[dateStr].includes(habitId);
}

function isCheckedIn(habitId, dateStr = todayStr()) {
  const data = getData();
  return !!(data.habits.checkins[dateStr] || []).includes(habitId);
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

// ── Ledger ───────────────────────────────────────────────

function getLedger() { return getData().ledger; }

function addRecord(type, amount, category, note = '', dateStr = todayStr()) {
  const data = getData();
  const record = { id: uid(), type, amount: parseFloat(amount), category, note, date: dateStr, createdAt: now() };
  data.ledger.records.unshift(record);
  setData({ ledger: data.ledger });
  return record;
}

function deleteRecord(recordId) {
  const data = getData();
  data.ledger.records = data.ledger.records.filter(r => r.id !== recordId);
  setData({ ledger: data.ledger });
}

function getBalance() {
  const data = getData();
  return data.ledger.records.reduce((acc, r) => {
    return acc + (r.type === 'income' ? r.amount : -r.amount);
  }, 0);
}

// ── Homepage ─────────────────────────────────────────────

function getHomepage() { return getData().homepage; }

function addShortcut(name, url, emoji = '🔗', color = '#8B8B8B') {
  const data = getData();
  const sh = { id: uid(), name, url, emoji, color };
  data.homepage.shortcuts.push(sh);
  setData({ homepage: data.homepage });
  return sh;
}

function deleteShortcut(shId) {
  const data = getData();
  data.homepage.shortcuts = data.homepage.shortcuts.filter(s => s.id !== shId);
  setData({ homepage: data.homepage });
}

function updateBgUrl(url) {
  const data = getData();
  data.homepage.bgUrl = url;
  setData({ homepage: data.homepage });
}

// ── 事件系统 ─────────────────────────────────────────────

function onUpdate(fn) { state.listeners.push(fn); return () => { state.listeners = state.listeners.filter(f => f !== fn); }; }
function notifyListeners(event, data) { state.listeners.forEach(fn => { try { fn(event, data); } catch(e) { console.error(e); } }); }
function notifySyncStatus(status) { notifyListeners('sync:' + status, {}); }

// ── Toast ────────────────────────────────────────────────

let _toastContainer = null;
function getToastContainer() {
  if (!_toastContainer) {
    _toastContainer = document.createElement('div');
    _toastContainer.className = 'toast-container';
    document.body.appendChild(_toastContainer);
  }
  return _toastContainer;
}

function showToast(text, type = 'info', duration = 3500) {
  const container = getToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;

  const icons = { success: '✅', error: '❌', info: '💡', warn: '⚠️' };
  toast.innerHTML = `
    <span class="toast__icon">${icons[type] || '💡'}</span>
    <span class="toast__text">${text}</span>
    <span class="toast__close">✕</span>
  `;

  toast.querySelector('.toast__close').onclick = () => removeToast(toast);
  container.appendChild(toast);

  if (duration > 0) setTimeout(() => removeToast(toast), duration);
  return toast;
}

function removeToast(toast) {
  if (!toast.parentNode) return;
  toast.classList.add('removing');
  setTimeout(() => toast.remove(), 260);
}

// ── 导出 ─────────────────────────────────────────────────

window.OtterHub = {
  init, login, logout, syncNow,
  isOnline,
  getData, setData,
  // 状态
  get state() { return state; },
  // Todo
  getTodo, addTask, toggleTask, deleteTask, addList, deleteList,
  // Habits
  getHabits, addHabit, deleteHabit, toggleCheckin, isCheckedIn, todayStr,
  // Ledger
  getLedger, addRecord, deleteRecord, getBalance,
  // Homepage
  getHomepage, addShortcut, deleteShortcut, updateBgUrl,
  // Events
  onUpdate,
  // UI
  showToast
};
