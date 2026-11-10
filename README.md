# H5 轻应用交互 · 校园问卷与趣味测试

智能交互技术与应用 · 实验三作业
作者：刘威　202401170148

一个 H5 站点，包含三个可交互的轻应用：

| 入口 | 说明 |
|---|---|
| `/` | 学生求职意向调查问卷（引导页）|
| `/fill.html` | 问卷填写页（单选 / 多选 / 下拉 / 输入）|
| `/result.html` | 提交结果页 |
| `/records.html` | 个人记录中心 |
| `/wuxing/` | 五行命格测试（趣味国风）|
| `/color/` | 人格色彩速测（20 题 MBTI）|

## 目录结构

```
h5-lightapps/
├── app.py                本地服务：静态托管 + 记录接口
├── requirements.txt      无第三方依赖
├── data/records.json     问卷记录（首次提交后自动生成）
└── static/               ← 站点根目录，可直接部署到 GitHub Pages
    ├── index.html
    ├── fill.html
    ├── result.html
    ├── records.html
    ├── assets/css/base.css
    ├── assets/js/common.js
    ├── wuxing/index.html
    └── color/index.html
```

## 本地运行（PyCharm）

1. PyCharm → Open → 选择本目录 `h5-lightapps`
2. 右侧提示“配置解释器”时，选本机 Python 3.9+
3. 打开 `app.py`，右键 → `Run 'app'`
4. 浏览器访问 <http://127.0.0.1:8000>

不需要 `pip install`，后端只用 Python 标准库。

## 部署到 GitHub Pages

`static/` 目录本身就是完整静态站点，推送后开启 Pages 即可：

```bash
git init
git add .
git commit -m "H5 轻应用实验三"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

然后在仓库 Settings → Pages 里把 Source 设为 `GitHub Actions`，
仓库自带的 `.github/workflows/pages.yml` 会自动发布 `static/`。

## 说明：两种环境都能跑

`assets/js/common.js` 会先尝试请求 `/api/records`：

- 请求成功 → 记录存到 `data/records.json`（本地服务模式）
- 请求失败 → 自动降级到 `localStorage`（GitHub Pages 纯静态模式）

因此同一套前端代码，在本地和线上表现一致，只是数据落点不同。
