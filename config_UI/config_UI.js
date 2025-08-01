// config_UI.js
// 配置界面前端逻辑

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('configForm');
  const msg = document.getElementById('msg');
  const loadBtn = document.getElementById('loadBtn');

  // 读取配置
  async function loadConfig() {
    msg.textContent = '正在读取配置...';
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      if (!data.success) throw new Error(data.msg || '读取失败');
      fillForm(data.config);
      msg.textContent = '配置读取成功';
    } catch (e) {
      msg.textContent = '读取失败：' + e.message;
    }
  }

  // 填充表单
  function fillForm(config) {
    form['account.username'].value = config.account?.username || '';
    form['account.password'].value = config.account?.password || '';
    form['account.edgedriver_path'].value = config.account?.edgedriver_path || '';
    form['account.reuse_local_login'].checked = !!config.account?.reuse_local_login;
    form['account.user_data_dir'].value = config.account?.user_data_dir || '';
    form['live.room_url'].value = config.live?.room_url || '';
    form['danmu.interval'].value = config.danmu?.interval || 5;
    form['danmu.interval_float'].value = config.danmu?.interval_float || 0;
    form['danmu.pool_weight'].value = config.danmu?.pool_weight || 1;
    // 弹幕池一号弹窗内容
    renderDanmuCard(config.danmu?.contents || []);
    // 弹幕池二号弹窗内容
    renderDanmu2Card(config.danmu_pool2?.pool || []);
    form['danmu_pool2.pool_weight'].value = config.danmu_pool2?.pool_weight || 1;
    form['feature.auto_refresh_on_fail'].checked = !!config.feature?.auto_refresh_on_fail;
  }

  // 表单转配置对象
  function formToConfig() {
    // 弹幕池一号
    const danmuContents = [];
    document.querySelectorAll('#danmuCardBody .danmu-item input[type="text"]').forEach(input => {
      if (input.value.trim()) danmuContents.push(input.value.trim());
    });
    // 弹幕池二号
    const danmu2Arr = [];
    document.querySelectorAll('#danmu2CardBody .danmu-item').forEach(row => {
      const content = row.querySelector('input[type="text"]').value.trim();
      const weight = Number(row.querySelector('input[type="number"]').value) || 1;
      if (content) danmu2Arr.push({ content, weight });
    });
    const config = {
      account: {
        username: form['account.username'].value,
        password: form['account.password'].value,
        edgedriver_path: form['account.edgedriver_path'].value,
        reuse_local_login: form['account.reuse_local_login'].checked,
        user_data_dir: form['account.user_data_dir'].value
      },
      live: {
        room_url: form['live.room_url'].value
      },
      danmu: {
        interval: Number(form['danmu.interval'].value),
        interval_float: Number(form['danmu.interval_float'].value),
        pool_weight: Number(form['danmu.pool_weight'].value),
        contents: danmuContents
      },
      danmu_pool2: {
        pool_weight: Number(form['danmu_pool2.pool_weight'].value),
        pool: danmu2Arr
      },
      feature: {
        auto_refresh_on_fail: form['feature.auto_refresh_on_fail'].checked
      }
    };
    return config;
  }

  // 保存配置
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    msg.textContent = '正在保存...';
    try {
      const config = formToConfig();
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ config })
      });
      const data = await res.json();
      if (!data.success) throw new Error(data.msg || '保存失败');
      msg.textContent = '保存成功！';
    } catch (e) {
      msg.textContent = '保存失败：' + e.message;
    }
  });

  loadBtn.addEventListener('click', loadConfig);
  loadConfig();

  // 弹幕池一号弹窗逻辑
  const danmuCard = document.getElementById('danmuCard');
  const editDanmuBtn = document.getElementById('editDanmuBtn');
  const danmuCardBody = document.getElementById('danmuCardBody');
  const danmuCardAdd = document.getElementById('danmuCardAdd');
  const danmuCardSave = document.getElementById('danmuCardSave');
  const danmuCardCancel = document.getElementById('danmuCardCancel');
  editDanmuBtn.addEventListener('click', () => {
    danmuCard.classList.add('show');
  });
  danmuCardCancel.addEventListener('click', () => {
    danmuCard.classList.remove('show');
  });
  danmuCardAdd.addEventListener('click', () => {
    addDanmuItem('');
  });
  danmuCardSave.addEventListener('click', () => {
    danmuCard.classList.remove('show');
  });
  function renderDanmuCard(arr) {
    danmuCardBody.innerHTML = '';
    (arr.length ? arr : ['']).forEach(content => addDanmuItem(content));
  }
  function addDanmuItem(val) {
    const row = document.createElement('div');
    row.className = 'danmu-item';
    row.innerHTML = `<input type="text" placeholder="弹幕内容" value="${val||''}" />
      <button type="button" class="remove-btn">删除</button>`;
    row.querySelector('.remove-btn').onclick = () => row.remove();
    danmuCardBody.appendChild(row);
  }

  // 弹幕池二号弹窗逻辑
  const danmu2Card = document.getElementById('danmu2Card');
  const editDanmu2Btn = document.getElementById('editDanmu2Btn');
  const danmu2CardBody = document.getElementById('danmu2CardBody');
  const danmu2CardAdd = document.getElementById('danmu2CardAdd');
  const danmu2CardSave = document.getElementById('danmu2CardSave');
  const danmu2CardCancel = document.getElementById('danmu2CardCancel');
  editDanmu2Btn.addEventListener('click', () => {
    danmu2Card.classList.add('show');
  });
  danmu2CardCancel.addEventListener('click', () => {
    danmu2Card.classList.remove('show');
  });
  danmu2CardAdd.addEventListener('click', () => {
    addDanmu2Item('', 1);
  });
  danmu2CardSave.addEventListener('click', () => {
    danmu2Card.classList.remove('show');
  });
  function renderDanmu2Card(arr) {
    danmu2CardBody.innerHTML = '';
    (arr.length ? arr : [{content:'',weight:1}]).forEach(item => addDanmu2Item(item.content, item.weight));
  }
  function addDanmu2Item(val, weight) {
    const row = document.createElement('div');
    row.className = 'danmu-item';
    row.innerHTML = `<input type="text" placeholder="弹幕内容" value="${val||''}" />
      <input type="number" min="1" value="${weight||1}" style="width:28px;margin-left:8px;text-align:center;" title="权重" />
      <button type="button" class="remove-btn">删除</button>`;
    row.querySelector('.remove-btn').onclick = () => row.remove();
    // 不再设置writing-mode，全部交由CSS控制
    danmu2CardBody.appendChild(row);
  }
});
