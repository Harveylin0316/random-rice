// 將數據庫文件作為模組導出
// 這樣 Netlify Functions 會自動包含它
const database = require('./restaurants_database.json');
module.exports = database;
