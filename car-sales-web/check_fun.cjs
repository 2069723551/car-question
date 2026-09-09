const { parse, compileTemplate } = require('@vue/compiler-sfc');
const fs = require('fs');
const src = fs.readFileSync('C:/Users/石鹤歌/Desktop/汽车销量预测系统-完整版/car-sales-web/src/views/FunView.vue', 'utf-8');
const { descriptor, errors } = parse(src, { filename: 'FunView.vue' });
if (errors.length) {
  for (const e of errors) console.log('PARSE ERR:', e.message, '| loc:', JSON.stringify(e.loc && e.loc.start));
} else {
  console.log('parse OK');
  const r = compileTemplate({ source: descriptor.template.content, filename: 'FunView.vue', id: 'x' });
  if (r.errors && r.errors.length) {
    for (const e of r.errors) console.log('TEMPLATE ERR:', e.message, '| loc:', JSON.stringify(e.loc && e.loc.start));
  } else {
    console.log('template compile OK');
  }
}
