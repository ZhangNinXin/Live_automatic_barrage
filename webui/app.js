function showModal(msg, onConfirm) {
  const modal = document.createElement('div');
  modal.className = 'ms-modal-mask';
  modal.innerHTML = `<div class="ms-modal"><div class="ms-modal-content">${msg}</div><div class="ms-modal-footer"><button class="ms-btn ms-primary" id="modalConfirmBtn">确定</button></div></div>`;
  document.body.appendChild(modal);
  document.getElementById('modalConfirmBtn').onclick = () => {
    document.body.removeChild(modal);
    if (onConfirm) onConfirm();
  };
}
const { createApp, ref, onMounted } = Vue;
createApp({
  setup() {
    const page = ref('login');
    const config = ref({});
    const output = ref('');
    const running = ref(false);
    const tab = ref('output');
    const statusMsg = ref('');
    function fetchConfig() {
      fetch('/api/config').then(r=>r.json()).then(res=>{if(res.success) config.value = res.config;});
    }
    function start() {
      showModal('确定要启动弹幕机器人吗？', () => {
        fetch('/api/start', {method:'POST'}).then(r=>r.json()).then(res=>{
          if(res.success) { running.value = true; statusMsg.value = '程序已启动'; fetchOutput(); }
          else statusMsg.value = res.msg || '启动失败';
        });
      });
    }
    function stop() {
      showModal('确定要终止弹幕机器人吗？', () => {
        fetch('/api/stop', {method:'POST'}).then(r=>r.json()).then(res=>{
          if(res.success) { running.value = false; statusMsg.value = '程序已终止'; }
          else statusMsg.value = res.msg || '终止失败';
        });
      });
    }
    function fetchOutput() {
      if (!running.value) return;
      fetch('/api/output').then(r=>r.json()).then(res=>{
        if(res.success) output.value += res.output;
        setTimeout(fetchOutput, 1200);
      });
    }
    function openConfig() {
      fetch('/api/open_config', {method:'POST'}).then(()=>{
        showModal('配置页已打开，请在新窗口中进行配置。');
      });
    }
    onMounted(fetchConfig);
    return { page, config, output, running, tab, statusMsg, start, stop, openConfig, fetchConfig };
  },
  template: `
    <div v-if="page==='login'" class="ms-card">
      <div class="ms-header"><span class="ms-title">快手弹幕机</span></div>
      <div style="margin-bottom:32px;">
        <button class="ms-btn" @click="page='main'">进入程序</button>
        <button class="ms-btn ms-secondary" @click="openConfig">打开配置页</button>
      </div>
    </div>
    <div v-else class="ms-card">
      <div class="ms-header">
        <span class="ms-title">仪表盘</span>
        <span class="ms-info">
          <span class="ms-label">直播间:</span>{{config.live?.room_url||'-'}}
          <span class="ms-label" style="margin-left:18px;">弹幕池权重:</span>{{config.danmu?.pool_weight||'-'}}
        </span>
        <span class="ms-status">{{statusMsg}}</span>
        <button class="ms-btn ms-secondary" style="margin-left:32px;" @click="openConfig">打开配置页</button>
      </div>
      <div style="margin-bottom:18px;">
        <button class="ms-btn" @click="start" :disabled="running">启动</button>
        <button class="ms-btn ms-danger" @click="stop" :disabled="!running">终止</button>
        <button class="ms-btn ms-secondary" @click="fetchConfig">刷新配置</button>
      </div>
      <div class="ms-tabs">
        <div class="ms-tab" :class="{active:tab==='output'}" @click="tab='output'">实时输出</div>
      </div>
      <div v-show="tab==='output'" class="ms-output">{{output}}</div>
    </div>
  `
}).mount('#app');
