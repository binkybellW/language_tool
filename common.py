import streamlit as st
import re
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import pandas as pd

def generate_wordcloud(analysis_text):
    remove_stop_words = st.checkbox('去除连接词', value=False, key='remove_stop_words_checkbox')
    
    try:
        # 将文本中的多个空格合并为单个空格
        text = ' '.join(analysis_text.split())
        
        if remove_stop_words:
            # 英文分词并去除连接词
            english_stop_words = {'is', 'an', 'of', 'to', 'and', 'that', 'can', 'has', 'in', 'like'}
            english_words = [word for word in re.findall(r'[A-Za-z]+', text) if word.lower() not in english_stop_words]
            
            # 中文分词并去除连接词
            chinese_stop_words = {'的', '和', '等', '与', '及', '在', '了', '给'}
            chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
            chinese_words = [word for word in jieba.lcut(chinese_text) if word not in chinese_stop_words]
            
            # 合并中英文词频统计
            all_words = english_words + chinese_words
            word_freq = Counter(all_words)
        else:
            # 不去除连接词的处理
            english_words = re.findall(r'[A-Za-z]+', text)
            chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
            chinese_words = jieba.lcut(chinese_text)
            all_words = english_words + chinese_words
            word_freq = Counter(all_words)
        
        # 创建词云图
        # 检查字体文件是否存在
        import os
        font_path = './app/static/Hiragino Sans GB.ttc'
        if not os.path.exists(font_path):
            st.warning(f'未找到字体文件: {font_path}，词云图可能无法正确显示中文')
        # 列出./app/static目录下的所有文件
        try:
            # 获取当前路径
            current_path = os.getcwd()
            st.write(f'当前路径: {current_path}')
            
            # 列出当前路径下的所有文件和文件夹
            current_files = os.listdir(current_path)
            st.write('当前目录下的文件和文件夹:')
            for item in current_files:
                # 判断是文件还是文件夹
                if os.path.isdir(os.path.join(current_path, item)):
                    st.write(f'📁 {item}')
                else:
                    st.write(f'📄 {item}')
            
            # 列出static目录下的文件
            static_path = './app/static'
            static_files = os.listdir(static_path)
            st.write(f'\nstatic目录 ({static_path}) 下的文件:')
            for file in static_files:
                st.write(f'📄 {file}')
                
        except Exception as e:
            st.error(f'无法读取目录: {str(e)}')
        wc = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            max_words=200,
            font_path='./app/static/Hiragino Sans GB.ttc',  # 使用支持中英文的字体
            random_state=42
        ).generate_from_frequencies(word_freq)
        
        # 显示词云图
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout(pad=0)
        
        # 在Streamlit中显示词云图
        st.pyplot(fig)
        
        # 提供下载词云图的选项
        img = io.BytesIO()
        plt.savefig(img, format='pdf')
        img.seek(0)
        
        st.download_button(
            label="下载词云图",
            data=img,
            file_name="wordcloud.pdf",
            mime="application/pdf"  # mime参数指定了文件的MIME类型，这里是PDF文件
        )
        plt.close()
    except Exception as e:
        st.error(f"生成词云图失败: {str(e)}")
        
        
        
def count_word_frequency(analysis_text):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        remove_punctuation = st.checkbox('去除标点符号')
    with col2:
        remove_stopwords = st.checkbox('去除连接词')
    with col3:
        remove_numbers = st.checkbox('去除数字')
    with col4:
        top_n = st.number_input('显示前N个词', min_value=1, value=20)
    words = jieba.lcut(analysis_text)
    
    if remove_punctuation:
        words = [w for w in words if not re.match(r'[^\w]', w)]
        
    if remove_stopwords:
        stopwords = ['的','了','和','是','在','我','有','就','不','都','而','及','与','着','或']
        words = [w for w in words if w not in stopwords]

    if remove_numbers:
        words = [w for w in words if not w.isdigit()]
    
    word_freq = Counter(words)
    freq_df = pd.DataFrame.from_dict(word_freq, orient='index', columns=['频次'])
    freq_df = freq_df.sort_values('频次', ascending=False)
    
    # 只保留前N个
    freq_df = freq_df.head(top_n)
    
    st.write('词频统计结果:')
    st.dataframe(freq_df)
    
    # 导出词频统计结果
    csv = freq_df.to_csv(encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="下载词频统计结果", 
        data=csv,
        file_name="word_frequency.csv",
        mime="text/csv"
    )
    
    
def count_characters(analysis_text):
    # 统计总字数
    char_count = len(analysis_text)
    word_count = len(analysis_text.split())
    
    
    # 计算除标点外的字符数
    no_punc_count = len([c for c in analysis_text if not re.match(r'[^\w\s]', c)])
    
    st.write(f'字符数: {char_count}')
    st.write(f'除标点外的字符数: {no_punc_count}')
    
    # 导出统计结果
    stats_dict = {'字符数': char_count, '词数': word_count}
    stats_df = pd.DataFrame([stats_dict])
    csv = stats_df.to_csv(encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="下载统计结果",
        data=csv,
        file_name="text_statistics.csv",
        mime="text/csv"
    )
