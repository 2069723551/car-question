const { parse, compileTemplate } = require('@vue/compiler-sfc');
const fs = require('fs');
const file = 'C:/Users/石鹤歌/Desktop/汽车销量预测系统-完整版/car-sales-web/src/views/FunView.vue';
const src = fs.readFileSync(file, 'utf-8');

// 手动切块：找到 script/template/style 边界
const s1 = src.indexOf('<script');
const s2 = src.indexOf('</script>');
const t1 = src.indexOf('<template>', s2);
const t2 = src.indexOf('</template>', t1);
const st1 = src.indexOf('<style');
console.log('script:', s1, s2, 'template:', t1, t2, 'style:', st1);
const tpl = src.slice(t1, t2 + 11);
console.log('tpl len:', tpl.length);

// 二分：注释掉后半部分
function test(content, label) {
  try {
    const r = compileTemplate({ source: content, filename: 'x.vue', id: 'x' });
    if (r.errors && r.errors.length) {
      console.log('ERR', label, r.errors[0].message, JSON.stringify(r.errors[0].loc && r.errors[0].loc.start));
      return false;
    }
    console.log('OK ', label);
    return true;
  } catch (e) {
    console.log('CRASH', label, String(e.message).slice(0, 120));
    return false;
  }
}

// 逐步测试
const half = Math.floor(tpl.length / 2);
// 后半部分是游戏4区域，先测前半（去掉游戏4）
const idxRace = tpl.indexOf('游戏4：公路赛车');
console.log('race idx in tpl:', idxRace);
test(tpl.slice(0, idxRace), '去掉游戏4');
test(tpl, '全部');
