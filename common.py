import streamlit as st
import re
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import pandas as pd

def generate_wordcloud(analysis_text):
    remove_stop_words = st.checkbox('去除停用词', value=False, key='remove_stop_words_checkbox')
    
    custom_stop_words = st.text_area(
        '自定义停用词（使用英文逗号 , 分隔，例如：的,和,etc,and）',
        value='',
        help='请使用英文逗号(,)分隔每个停用词，支持中英文混合输入',
        key='custom_stop_words_textarea'
    )
    
    try:
        # 将文本中的多个空格合并为单个空格
        text = ' '.join(analysis_text.split())
        
        if remove_stop_words:
            # 更新停用词列表
            stop_words = set(word.strip() for word in custom_stop_words.split(',') if word.strip())
            stop_words.update(['我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', 
                               '的', '了', '和', '在', '是', '不', '也', '有', '对', '到', '说', 
                               '看', '很', '都', '这', '那', '什么', '就', '人', '因为', '怎么', 
                               '一个', '而', '但', '会', '能', '让', '如果', '又', '用', '自己', 
                               '多', '没', '为', '去', '然后', '这样', '那样', '真的', '所以', 
                               '其实', '并', '吧', '吗', '呢', '就是', '而且', '或者', '可以', 
                               '可能', '像', '要', '比如', '从', '更', '这儿', '那儿', '那么', '如此'])
            
            # 分别处理英文和中文
            english_words = [word for word in re.findall(r'[A-Za-z]+', text) if word.lower() not in stop_words]
            
            chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
            chinese_words = [word for word in jieba.lcut(chinese_text) if word not in stop_words]
            
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
        wc = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            max_words=200,
            font_path='./static/Hiragino Sans GB.ttc',  # 使用支持中英文的字体
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
        remove_stopwords = st.checkbox('去除停用词')
    with col3:
        remove_numbers = st.checkbox('去除数字')
    with col4:
        top_n = st.number_input('显示前N个词', min_value=1, value=20)
    words = jieba.lcut(analysis_text)
    
    if remove_punctuation:
        words = [w for w in words if not re.match(r'[^\w]', w)]
        
    if remove_stopwords:
        stopwords = ['我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们', 
                     '的', '了', '和', '在', '是', '不', '也', '有', '对', '到', '说', 
                     '看', '很', '都', '这', '那', '什么', '就', '人', '因为', '怎么', 
                     '一个', '而', '但', '会', '能', '让', '如果', '又', '用', '自己', 
                     '多', '没', '为', '去', '然后', '这样', '那样', '真的', '所以', 
                     '其实', '并', '吧', '吗', '呢', '就是', '而且', '或者', '可以', 
                     '可能', '像', '要', '比如', '从', '更', '这儿', '那儿', '那么', '如此']
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

def split_words(analysis_text):
    st.subheader('分词结果')
    
    try:
        # 将文本中的多个空格合并为单个空格
        text = ' '.join(analysis_text.split())
        
        # 分别处理英文和中文
        # 英文：按空格分词，保留标点
        english_pattern = r'[A-Za-z]+(?:\'[A-Za-z]+)*|[.,!?;]'
        english_words = re.findall(english_pattern, text)
        
        # 中文：使用jieba分词
        chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', text))
        chinese_words = jieba.lcut(chinese_text)
        
        # 合并结果
        all_words = english_words + chinese_words
        
        # 显示分词结果
        st.text_area(
            '分词结果（词语间以空格分隔）：',
            value=' '.join(all_words),
            height=200,
            key='split_words_result'
        )
        
        # 提供下载选项
        result_str = ' '.join(all_words)
        st.download_button(
            label="下载分词结果",
            data=result_str.encode('utf-8'),
            file_name="split_words_result.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"分词失败: {str(e)}")
