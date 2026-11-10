/* ============================================================
   common.js —— 公共工具：存储、接口、提示
   设计要点：同一套代码在「本地 Python 服务」与「GitHub Pages 静态托管」
   两种环境下都能工作——优先走后端接口，后端不可用时自动降级 localStorage。
   ============================================================ */

(function (global) {
  "use strict";

  var STORE_KEY = "h5_survey_records_v1";
  var UID_KEY = "h5_survey_uid_v1";
  var API_TIMEOUT = 1500;

  /* ---------- 本机标识：用于区分不同填写人 ---------- */
  function uid() {
    var id = localStorage.getItem(UID_KEY);
    if (!id) {
      id = "u_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
      localStorage.setItem(UID_KEY, id);
    }
    return id;
  }

  /* ---------- 本地存储读写 ---------- */
  function readLocal() {
    try {
      return JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function writeLocal(list) {
    localStorage.setItem(STORE_KEY, JSON.stringify(list.slice(0, 50)));
  }

  /* ---------- 带超时的 fetch ---------- */
  function fetchWithTimeout(url, opts) {
    opts = opts || {};
    var controller = new AbortController();
    var timer = setTimeout(function () { controller.abort(); }, API_TIMEOUT);
    opts.signal = controller.signal;
    return fetch(url, opts).finally(function () { clearTimeout(timer); });
  }

  /* ---------- 记录接口：读 ---------- */
  function getRecords() {
    return fetchWithTimeout("/api/records?client=" + encodeURIComponent(uid()), {})
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d || !d.ok) throw new Error("bad response");
        return { records: d.records || [], source: "server" };
      })
      .catch(function () {
        return { records: readLocal(), source: "local" };
      });
  }

  /* ---------- 记录接口：写 ---------- */
  function saveRecord(record) {
    record.client = uid();
    var list = readLocal();
    list.unshift(record);
    writeLocal(list);

    return fetchWithTimeout("/api/records", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record)
    })
      .then(function (r) { return r.json(); })
      .then(function (d) { return d && d.ok ? "server" : "local"; })
      .catch(function () { return "local"; });
  }

  /* ---------- 提示条 ---------- */
  var toastTimer = null;
  function toast(msg) {
    var el = document.querySelector(".toast");
    if (!el) {
      el = document.createElement("div");
      el.className = "toast";
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add("is-show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove("is-show"); }, 2000);
  }

  /* ---------- 时间格式化 ---------- */
  function fmtTime(ts) {
    var d = new Date(ts);
    var p = function (n) { return n < 10 ? "0" + n : "" + n; };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
      " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }

  global.H5 = {
    uid: uid,
    getRecords: getRecords,
    saveRecord: saveRecord,
    toast: toast,
    fmtTime: fmtTime
  };
})(window);
