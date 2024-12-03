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

from common import generate_wordcloud,count_word_frequency,count_characters,split_words


example_text="人工智能（Artificial Intelligence, AI）是计算机科学的一个分支，旨在创建能够像人类一样思考和学习的智能机器。AI技术包括机器学习（Machine Learning）、自然语言处理（Natural Language Processing）和计算机视觉（Computer Vision）等。随着科技的进步，AI在各个领域的应用越来越广泛，例如自动驾驶（Autonomous Driving）、医疗诊断（Medical Diagnosis）和智能客服（Intelligent Customer Service）等。AI的快速发展不仅改变了我们的生活方式，也引发了关于伦理和隐私的广泛讨论。未来，AI有望在教育、金融、制造业等更多领域发挥重要作用，推动社会的进一步发展。AI的潜力是无限的，它不仅可以提高生产效率，还可以通过分析大量数据来提供更好的决策支持。随着AI算法的不断优化和计算能力的提升，我们可以期待AI在解决复杂问题和创新方面带来更多突破。"

# 设置页面配置
st.set_page_config(
    page_title="语言分析工具",
    page_icon="📚",
    layout="wide"
)

# 导航栏
st.sidebar.title('导航栏')
page = st.sidebar.radio(
    '选择页面',
    ['首页', 'B站弹幕分析', '语料清洗', '词频统计与词云图', '语料资源整合']
)

# 首页
if page == '首页':
    st.title('语言分析工具 📚')
    
    st.write("""
    本工具提供以下功能：
    - 🎬 B站弹幕分析：支持B站视频弹幕获取和分析，包含词频统计、情感分析、词云图等功能
    - 🧹 语料清洗：提供文本预处理和分词功能
    - 📊 词频统计与词云图：对文本进行词频统计分析并生成词云图
    
    请使用左侧导航栏选择所需功能。
    """)
    
    # 展示一些示例或使用说明
    with st.expander("💡 使用说明"):
        st.write("""
        1. 所有功能都支持文件导入导出
        2. 支持的文件格式：TXT, CSV, XLSX
        3. 建议单次处理文本大小不超过10MB
        """)
    
    # 添加首页图片，设置宽度为800像素
    st.image('static/LPT.png', width=800)


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

                            # 添加显示各类情感弹幕的选项
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

# 语料资源整合部分
elif page == '语料资源整合':
    st.title('语料资源整合 📚')
    
    st.markdown("""
    <div style='text-align: center; padding: 10px; color: #566573;'>
        为语言研究提供丰富的语料来源
    </div>
    """, unsafe_allow_html=True)
    
    # 分类展示
    categories = {
        "社交媒体语料": [
            {
                "name": "Twitter 数据集",
                "type": "推文文本、评论、转发、点赞数",
                "usage": "语言流行趋势、网络语体分析、情感变化研究",
                "link": "https://developer.twitter.com/en/docs"
            },
            {
                "name": "Reddit 讨论数据",
                "type": "主题帖、评论、投票数据",
                "usage": "社区讨论语言分析、用户互动语料研究",
                "link": "https://www.reddit.com/dev/api/"
            }
        ],
        "学术文献语料": [
            {
                "name": "PubMed Central",
                "type": "医学文献的标题、摘要、关键词",
                "usage": "医学术语研究、学术写作分析",
                "link": "https://www.ncbi.nlm.nih.gov/pmc/"
            },
            {
                "name": "ACL Anthology",
                "type": "学术论文的标题、摘要、关键词",
                "usage": "语言学研究、学术写作分析",
                "link": "https://www.aclweb.org/anthology/"
            }
        ]
    }
    
    for category, apis in categories.items():
        st.subheader(category)
        for api in apis:
            st.markdown(f"**{api['name']}**")
            st.write(f"语料类型：{api['type']}")
            st.write(f"用途：{api['usage']}")
            st.write(f"[访问API]({api['link']})")
            st.markdown("---")
