import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter
import jieba
import io
import requests
from snownlp import SnowNLP
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import tempfile
import copy

from common import generate_wordcloud,count_word_frequency,count_characters,split_words,text_annotation


example_text="人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，旨在创建能够像人类一样思考和学习的智能机器。AI技术包括机器学习（Machine Learning）、自然语言处理（Natural Language Processing）和计算机视觉（Computer Vision）等。随着科技的进步，AI在各个领域的应用越来越广泛，例如自动驾驶（Autonomous Driving）、医疗诊断（Medical Diagnosis）和智能客服（Intelligent Customer Service）等。AI的快速发展不仅改变了我们的生活方式，也引发了关于伦理和隐私的广泛讨论。未来，AI有望在教育、金融、制造业等更多领域发挥重要作用，推动社会的进一步发展。AI的潜力是无限的，它不仅可以提高生产效率，还可以通过分析大量数据来提供更好的决策支持。随着AI算法的不断优化和计算能力的提升，我们可以期待AI在解决复杂问题和创新方面带来更多突破。"

# 设置页面配置
st.set_page_config(
    page_title="语言分析工具",
    page_icon="📚",
    layout="wide"
)

# 添加自定义CSS样式
st.markdown("""
<style>
    /* 侧边栏背景 */
    .sidebar .sidebar-content {
        background-color: rgba(255, 192, 192, 0.1);  /* 非常淡的透明红色 */
        padding: 20px;
        backdrop-filter: blur(5px);  /* 添加模糊效果 */
    }
    
    /* 导航按钮样式 */
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        display: block;
        padding: 12px 20px;
        margin: 8px 0;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.8);  /* 半透明白色背景 */
        border: 1px solid rgba(255, 192, 192, 0.3);  /* 淡红色边框 */
        color: #333;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    /* 导航按钮悬停效果 */
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 228, 228, 0.5);  /* 淡红色悬停背景 */
        border-color: rgba(255, 192, 192, 0.5);
        transform: translateX(5px);
    }
    
    /* 选中状态样式 */
    div.row-widget.stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div {
        background-color: rgba(255, 128, 128, 0.8);  /* 选中状态的红色 */
        border-color: rgba(255, 128, 128, 0.8);
    }
    
    /* 选中文本样式 */
    div.row-widget.stRadio > div[role="radiogroup"] > label > div:last-child {
        color: #333;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* 文本悬停效果 */
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover > div:last-child {
        color: rgba(255, 64, 64, 0.8);  /* 文字悬停时的红色 */
    }
    
    /* 标题和其他文字的悬停效果 */
    .sidebar .sidebar-content h1:hover,
    .sidebar .sidebar-content h2:hover,
    .sidebar .sidebar-content h3:hover,
    .sidebar .sidebar-content p:hover {
        color: rgba(255, 64, 64, 0.8);
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# 导航栏
st.sidebar.title('导航菜单')
st.sidebar.markdown('---')

# 简化的导航选项
pages = ['首页', 'B站弹幕分析', '语料清洗', '词频统计与词云图', '标注工具']

page = st.sidebar.radio(
    '选择功能',
    pages
)

# 添加页脚
st.sidebar.markdown('---')
st.sidebar.markdown('### 关于')
st.sidebar.markdown('语言分析工具 v1.0')
st.sidebar.markdown('Made with ❤️ by Shan')

# 首页
if page == '首页':
    st.markdown("""
    <style>
    .big-font {
        font-size: 2.8em !important;
        font-weight: bold;
        color: #333333;
        text-align: center;
        margin-bottom: 0.5em;
        padding: 10px;
    }
    .feature-card {
        padding: 15px;
        border-radius: 12px;
        background-color: #f8f9fa;  /* 浅灰背景 */
        /* 或者可以选择：
        background-color: #e8f4f8;  浅蓝背景
        background-color: #f0f7f4;  浅绿背景
        background-color: #fff5f5;  浅粉背景
        */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        transition: all 0.3s ease;
        text-align: center;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
    }
    .feature-icon {
        font-size: 2em;
        margin-bottom: 5px;
        color: #333333;
    }
    .feature-title {
        font-size: 1.3em;
        font-weight: bold;
        color: #333333;
        margin-bottom: 5px;
    }
    .feature-description {
        color: #444;
        font-size: 1em;
        line-height: 1.2;
        text-align: center;
    }
    .feature-description ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }
    .feature-description li {
        margin: 3px 0;
        padding: 2px;
    }
    .intro-text {
        text-align: center;
        margin-bottom: 1.5em;
        font-size: 1.1em;
        color: #444;
    }
    .usage-guide {
        margin-top: 1.5em;
        padding: 20px;
        border-radius: 12px;
        background-color: #f8f9fa;
    }
    .usage-guide h3 {
        color: #155799;
        margin-bottom: 10px;
    }
    .usage-guide ol {
        font-size: 1em;
        line-height: 1.4;
        color: #444;
        margin: 0;
        padding-left: 20px;
    }
    .footer {
        margin-top: 1.5em;
        text-align: center;
        color: #666;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)



    # 标题
    st.markdown('<p class="big-font">语言分析工具集 📚 </p>', unsafe_allow_html=True)

    # 简介
    st.markdown('<div class="intro-text">集成了多种语言分析工具，助您更好地分析和理解文本数据。</div>', 
                unsafe_allow_html=True)

    # 功能卡片
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">文本统计分析</div>
            <div class="feature-description">
                <ul>
                    <li>• 词频统计与可视化</li>
                    <li>• 字符统计分析</li>
                    <li>• 词云图生成</li>
                    <li>• 数据导出功能</li>
                </ul>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🧹</div>
            <div class="feature-title">文本预处理</div>
            <div class="feature-description">
                <ul>
                    <li>• 去除标点符号</li>
                    <li>• 去除停用词</li>
                    <li>• 分词处理</li>
                    <li>• 自定义处理选项</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎬</div>
            <div class="feature-title">B站弹幕分析</div>
            <div class="feature-description">
                <ul>
                    <li>• 弹幕数据提取</li>
                    <li>• 情感倾向分析</li>
                    <li>• 热点内容识别</li>
                    <li>• 互动程度评估</li>
                </ul>
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-icon">🏷️</div>
            <div class="feature-title">文本标注工具</div>
            <div class="feature-description">
                <ul>
                    <li>• 词语级标注</li>
                    <li>• 句子级标注</li>
                    <li>• 多种标注模式</li>
                    <li>• 标注结果导出</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 使用说明
    st.markdown("""
    <div class="usage-guide">
        <h3>💡 使用说明</h3>
        <ol>
            <li>从左侧菜单选择需要使用的功能</li>
            <li>按照界面提示输入或上传文本数据</li>
            <li>设置相应的分析参数</li>
            <li>查看分析结果并下载</li>
        </ol>
    </div>
    
    <div class="footer">
        <p>如有问题或建议，欢迎反馈</p>
        <p>Version 1.0.0</p>
    </div>
    """, unsafe_allow_html=True)


# B站弹幕分析部分
elif page == 'B站弹幕分析':
    st.title('B站弹幕分析 🎬')
    
    # 添加刷新按钮
    refresh_button = st.button('刷新', type='primary')
    if refresh_button:
        st.session_state['video_url'] = ""
    
    # 输入B站视频URL
    video_url = st.text_input('请输入B站视频URL:', key='video_url')
    if video_url:
        try:
            # 获取视频信息
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.bilibili.com'
            }
            
            response = requests.get(video_url, headers=headers)
            response.raise_for_status()
            
            # 获取cid
            cid_match = re.search(r'"cid":(\d+)', response.text)
            if not cid_match:
                st.error("无法在页面中找到cid")
            else:
                cid = cid_match.group(1)
                
                # 获取弹幕数据
                danmaku_url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={cid}'
                response = requests.get(danmaku_url, headers=headers)
                content = response.content.decode('utf-8')
                
                pattern = r'<d p="([0-9.]+),.*?">(.*?)</d>'
                matches = re.findall(pattern, content)
                
                if not matches:
                    st.warning("未找到弹幕")
                else:
                    danmaku_list = []
                    for time_str, text in matches:
                        seconds = float(time_str)
                        minutes = int(seconds // 60)
                        remaining_seconds = int(seconds % 60)
                        formatted_time = f"{minutes:02d}:{remaining_seconds:02d}"
                        
                        danmaku_list.append({
                            'time': formatted_time,
                            'time_seconds': seconds,
                            'text': text.strip()
                        })
                    # 按时间排序
                    danmaku_list.sort(key=lambda x: x['time_seconds'])
                    
                    # 显示弹幕数据
                    st.write(f"共获取到 {len(danmaku_list)} 条弹幕")
                    
                    # 显示弹幕选项
                    show_danmaku = st.checkbox('显示弹幕内容')
                    if show_danmaku:
                        display_count = st.number_input('显示弹幕数量', 
                                                      min_value=1, 
                                                      max_value=len(danmaku_list),
                                                      value=min(10, len(danmaku_list)))
                        
                        # 显示指定数量的弹幕
                        st.write('弹幕内容:')
                        with st.expander("点击展开查看弹幕"):
                            container = st.container()
                            scroll_height = min(400, display_count * 50)  # 根据显示数量动态调整高度
                            with container:
                                for item in danmaku_list[:display_count]:
                                    st.markdown(f"<div style='margin-bottom:10px'>{item['time']}: {item['text']}</div>", 
                                              unsafe_allow_html=True)
                            # 设置容器的最大高度和滚动
                            st.markdown(f"""
                                <style>
                                    [data-testid="stExpander"] div.stMarkdown {{
                                        max-height: {scroll_height}px;
                                        overflow-y: scroll;
                                    }}
                                </style>
                                """, unsafe_allow_html=True)
                    # 分析选项
                    analysis_type = st.multiselect(
                        '选择分析类型',
                        ['词频统计', '情感分析', '词云图', '时间分布']
                    )
                    
                    if '词频统计' in analysis_type:
                        st.subheader('📊 词频统计分析')
                        with st.spinner('正在进行词频统计...'):
                            texts = [item['text'] for item in danmaku_list]
                            count_word_frequency(' '.join(texts))
                            
                    if '情感分析' in analysis_type:
                        st.subheader('😊 情感分析')
                        st.info('注意: 当前情感分析模型仍有待提升,分析结果仅供参考。')
                        with st.spinner('正在进行情感分析...'):
                            texts = [item['text'] for item in danmaku_list]
                            sentiments = []
                            danmaku_sentiments = []  # 存储弹幕和对应的情感值
                            for text in texts:
                                try:
                                    sentiment = SnowNLP(text).sentiments
                                    sentiments.append(sentiment)
                                    danmaku_sentiments.append({'text': text, 'sentiment': sentiment})
                                except:
                                    continue
                            
                            # 对弹幕按情感分类
                            positive = [d['text'] for d in danmaku_sentiments if d['sentiment'] > 0.6]
                            neutral = [d['text'] for d in danmaku_sentiments if 0.4 <= d['sentiment'] <= 0.6]
                            negative = [d['text'] for d in danmaku_sentiments if d['sentiment'] < 0.4]
                            
                            sentiment_dist = {
                                '积极': len(positive),
                                '中性': len(neutral),
                                '消极': len(negative)
                            }
                            
                            st.write('情感分析结果:')
                            sentiment_df = pd.DataFrame([sentiment_dist]).T
                            sentiment_df.columns = ['数量']
                            st.dataframe(sentiment_df)

                            # 添加显示各类情感幕的选项
                            show_examples = st.checkbox('显示情感分类弹幕示例')
                            if show_examples:
                                display_count = st.number_input('每类显示条数', min_value=1, value=5)
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.write('😊 积极弹幕:')
                                    for text in positive[:display_count]:
                                        st.text(text)
                                with col2:
                                    st.write('😐 中性弹幕:')
                                    for text in neutral[:display_count]:
                                        st.text(text)
                                with col3:
                                    st.write('😞 消极弹幕:')
                                    for text in negative[:display_count]:
                                        st.text(text)
                    if '词云图' in analysis_type:
                        st.subheader('☁️ 词云图生成')
                        with st.spinner('正在生成词云图...'):
                            texts = [item['text'] for item in danmaku_list]
                            generate_wordcloud(' '.join(texts))
                            
                    if '时间分布' in analysis_type:
                        st.subheader('📈 时间分布分析')
                        with st.spinner('正在分析时间分布...'):
                            times = [item['time_seconds'] for item in danmaku_list]
                            fig, ax = plt.subplots(figsize=(12, 6))
                            ax.hist(times, bins=20, color='skyblue', edgecolor='black')
                            ax.set_xlabel('Video Time (seconds)', fontsize=12, fontname='Times New Roman')
                            ax.set_ylabel('Number of Comments', fontsize=12, fontname='Times New Roman')
                            ax.set_title('Time Distribution of Comments', fontsize=14, pad=15, fontname='Times New Roman')
                            ax.grid(True, linestyle='--', alpha=0.7)
                            plt.tight_layout()
                            st.pyplot(fig)
                            
                            # 提供下载时间分布图的选项
                            img = io.BytesIO()
                            plt.savefig(img, format='pdf')
                            img.seek(0)
                            
                            st.download_button(
                                label="下载时间分布图",
                                data=img,
                                file_name="time_distribution.pdf",
                                mime="application/pdf"
                            )
                            plt.close()
                    # 导出选项
                    export_format = st.selectbox(
                        '💾 选择弹幕导出格式',
                        ['CSV', 'Excel']
                    )
                    
                    if export_format == 'CSV':
                        df = pd.DataFrame(danmaku_list)
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="下载CSV文件",
                            data=csv,
                            file_name="danmaku.csv",
                            mime="text/csv"
                        )
                    else:
                        df = pd.DataFrame(danmaku_list)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                            df.to_excel(tmp.name, index=False)
                            with open(tmp.name, 'rb') as f:
                                excel_data = f.read()
                            st.download_button(
                                label="下载Excel文件",
                                data=excel_data,
                                file_name="danmaku.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                            
        except Exception as e:
            st.error(f"获取弹幕失败: {str(e)}")

# 语料清洗部分
elif page == '语料清洗':
    st.title('语料清洗 🧹')
    
    if '示例文本' not in st.session_state:
        st.session_state['示例文本'] = ""
        
        # 添加刷新按钮
    refresh_button = st.button('刷新', type='primary')
    if refresh_button:
        st.session_state['示例文本'] = ""
        text_to_clean = ""


    if st.button('生成示例文本'):
        st.session_state['示例文本'] = example_text
        text_to_clean = st.session_state['示例文本']
    
    if st.session_state['示例文本']:
        st.write('生成的示例文本:')
        st.text_area('示例文本', st.session_state['示例文本'], height=200)
        text_to_clean = st.session_state['示例文本']
    else:
        # 文件上传
        uploaded_file = st.file_uploader("上传要分析的文件", type=['txt', 'csv'])
        
        if uploaded_file is not None:
            text_to_clean = uploaded_file.read().decode()
        else:
            text_to_clean = st.text_area('或直接输入要分析的文本:', height=200)
    
    if text_to_clean:
        # 清洗选项
        col1, col2 = st.columns(2)
        with col1:
            remove_punct = st.checkbox('删除标点符号')
            remove_numbers = st.checkbox('删除数字')
        with col2:
            to_lowercase = st.checkbox('转换为小写')
            remove_spaces = st.checkbox('删除多余空格')
        
        # 使用session_state来保存清洗后的文本
        if 'cleaned_text' not in st.session_state:
            st.session_state.cleaned_text = None
            
        if st.button('开始清洗'):
            # 执行清洗
            cleaned_text = text_to_clean
            if remove_punct:
                cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
            if remove_numbers:
                cleaned_text = re.sub(r'\d+', '', cleaned_text)
            if to_lowercase:
                cleaned_text = cleaned_text.lower()
            if remove_spaces:
                cleaned_text = ' '.join(cleaned_text.split())
            st.session_state.cleaned_text = cleaned_text
        
        if st.session_state.cleaned_text is not None:
            st.subheader('清洗后的文本:')
            st.text_area('结果', st.session_state.cleaned_text, height=200)
            
            # 添加分词功能
            if st.button('进行分词'):
                split_words(st.session_state.cleaned_text)
            
            # 保持现有的下载功能
            tet_res = st.session_state.cleaned_text.encode()
            st.download_button(
                label="下载清洗后的文本", 
                data=tet_res,
                file_name="cleaned_text.txt",
                mime="text/plain"
            )

# 词频统计与词云图部分（原语言分析部分）
elif page == '词频统计与词云图':
    st.title('词频统计与词云图📊')
    
    if '示例文本' not in st.session_state:
        st.session_state['示例文本'] = ""
        
        # 添加刷新按钮
    refresh_button = st.button('刷新', type='primary')
    if refresh_button:
        st.session_state['示例文本'] = ""
        analysis_text = ""


    if st.button('生成示例文本'):
        st.session_state['示例文本'] = example_text
        analysis_text = st.session_state['示例文本']
    
    if st.session_state['示例文本']:
        st.write('生成的示例文本:')
        st.text_area('示例文本', st.session_state['示例文本'], height=200)
        analysis_text = st.session_state['示例文本']
    else:
        # 文件上传
        uploaded_file = st.file_uploader("上传要分析的文件", type=['txt', 'csv'])
        
        if uploaded_file is not None:
            analysis_text = uploaded_file.read().decode()
        else:
            analysis_text = st.text_area('或直接输入要分析的文本:', height=200)
    

    if analysis_text:

        # 分析选项
        analysis_type = st.multiselect(
            '选择分析类型',
            ['词频统计', '字符统计', '词云图']
        )
        
        if '词频统计' in analysis_type:
            st.subheader('📊 词频统计分析')
            
            with st.spinner('正在进行词频统计...'):
                count_word_frequency(analysis_text)
        if '字符计' in analysis_type:
            st.subheader('📝 字符统计分析')
            with st.spinner('正在进行字符统计...'):
                count_characters(analysis_text)

        
        if '词云图' in analysis_type:
            st.subheader('☁️ 词云图生成')
            with st.spinner('正在生成词云图...'):
                generate_wordcloud(analysis_text)

# 添加标注工具页面的处理逻辑
elif page == '标注工具':
    st.title('文本标注工具 🏷️')
    
    # 添加刷新按钮
    refresh_button = st.button('刷新', type='primary')
    if refresh_button:
        st.session_state['示例文本'] = ""
        annotation_text = ""

    # 文本输入部分
    if st.button('生成示例文本'):
        st.session_state['示例文本'] = example_text
        annotation_text = st.session_state['示例文本']
    
    if st.session_state.get('示例文本'):
        st.write('生成的示例文本:')
        st.text_area('示例文本', st.session_state['示例文本'], height=200)
        annotation_text = st.session_state['示例文本']
    else:
        # 文件上传
        uploaded_file = st.file_uploader("上传要标注的文件", type=['txt', 'csv'])
        
        if uploaded_file is not None:
            annotation_text = uploaded_file.read().decode()
        else:
            annotation_text = st.text_area('或直接输入要标注的文本:', height=200)

    if annotation_text:
        # 调用标注功能
        text_annotation(annotation_text)
