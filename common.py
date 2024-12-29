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
                               '可能', '像', '要', '比如', '从', '更', '这儿', '那儿', '那么','等','如此'])
            
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
                     '可能', '像', '要', '比如', '从', '更', '这儿', '那儿', '那么','等','如此']
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
    # 1. 总字符数（不包括空格和换行符）
    char_count_no_space = len([c for c in analysis_text if not c.isspace()])
    
    # 2. 有效字符数（不包括空格、换行符和标点符号）
    valid_chars = len([c for c in analysis_text if c.isalnum() or '\u4e00' <= c <= '\u9fff'])
    
    # 3. 分类统计
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', analysis_text))
    english_chars = len(re.findall(r'[a-zA-Z]', analysis_text))
    numbers = len(re.findall(r'\d', analysis_text))
    spaces = len(re.findall(r'\s', analysis_text))
    punctuation = len([c for c in analysis_text if re.match(r'[^\w\s]', c)])
    
    # 4. 词数统计
    # 英文词数
    english_words = len([word for word in analysis_text.split() if re.match(r'[a-zA-Z]+', word)])
    # 中文词数（使用jieba分词）
    chinese_text = ''.join(re.findall(r'[\u4e00-\u9fff]+', analysis_text))
    chinese_words = len(jieba.lcut(chinese_text))
    total_words = english_words + chinese_words
    
    # 显示统计结果
    st.write("### 字符统计")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**基本统计：**")
        st.write(f'总字符数（包含所有字符）: {len(analysis_text)}')
        st.write(f'总字符数（不含空白字符）: {char_count_no_space}')
        st.write(f'有效字符数（仅字母、数字、汉字）: {valid_chars}')
        st.write(f'总词数: {total_words}')
    
    with col2:
        st.markdown("**详细分类：**")
        st.write(f'中文字符数: {chinese_chars}')
        st.write(f'英文字符数: {english_chars}')
        st.write(f'数字个数: {numbers}')
        st.write(f'空格及换行数: {spaces}')
        st.write(f'标点符号数: {punctuation}')
    
    # 导出统计结果
    stats_dict = {
        '总字符数（全部）': len(analysis_text),
        '总字符数（不含空白）': char_count_no_space,
        '有效字符数': valid_chars,
        '总词数': total_words,
        '中文字符数': chinese_chars,
        '英文字符数': english_chars,
        '数字个数': numbers,
        '空格及换行数': spaces,
        '标点符号数': punctuation,
        '中文词数': chinese_words,
        '英文词数': english_words
    }
    stats_df = pd.DataFrame([stats_dict])
    csv = stats_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
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

def text_annotation(text):
    """文本标注功能"""
    if not text:
        st.warning('请先输入要标注的文本')
        return
    
    # 使用session_state存储处理后的文本
    if 'processed_text' not in st.session_state:
        st.session_state.processed_text = text
    
    # 文本预处理选项
    st.write("### 文本预处理选项")
    col1, col2, col3 = st.columns(3)
    with col1:
        remove_punctuation = st.checkbox('去除标点符号（保留句号）', key='annotation_remove_punct')
    with col2:
        remove_spaces = st.checkbox('去除多余空格', key='annotation_remove_space')
    with col3:
        remove_numbers = st.checkbox('去除数字', key='annotation_remove_num')
    
    # 更新分词处理
    def process_text(text):
        # 先处理英文单词
        # 在英文单词之间添加空格
        text = re.sub(r'([a-zA-Z])([A-Z])', r'\1 \2', text)  # 处理驼峰命名
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)     # 处理字母和数字
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)     # 处理数字和字母
        
        # 使用jieba分词，但保留英文单词的完整性
        words = []
        for segment in text.split():  # 先按空格分割
            if re.match(r'^[a-zA-Z]+$', segment):  # 如果是纯英文单词
                words.append(segment)
            else:  # 对非英文部分使用jieba分词
                words.extend(jieba.lcut(segment))
        return words

    # 处理文本
    if text:
        st.session_state.processed_text = text
        words = process_text(text)
        st.session_state.words = words
        
    # 文本预处理
    if st.button("应用预处理", key='apply_preprocessing'):
        processed_text = text
        if remove_punctuation:
            # 保留句号、感叹号、问号等分句标点
            processed_text = re.sub(r'[^\w\s。！？!?.]', '', processed_text)
        if remove_spaces:
            # 合并多个空格为单个空格并移除英文单词之间的空格
            words = processed_text.split()
            processed_text = ''.join(words)
        if remove_numbers:
            processed_text = re.sub(r'\d+', '', processed_text)
        
        # 保存处理后的文本
        st.session_state.processed_text = processed_text
        st.success('预处理完成！')
    
    # 显示当前要处理的文本
    st.write("### 当前文本")
    st.text_area("文本内容：", st.session_state.processed_text, height=100, key='current_text_display')
    
    # 分句
    sentences = re.split(r'([。！？.!?])', st.session_state.processed_text)
    sentences = [''.join(i) for i in zip(sentences[0::2], sentences[1::2] + [''])]
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # 使用info显示分句结果
    st.info(f"✂️ 文本已被分割为 {len(sentences)} 个句子")
    
    # 使用明显的分隔线和样式突出标注模式选择
    st.markdown("---")
    st.markdown("""
    <style>
    .annotation-header {
        font-size: 1.5em;
        font-weight: bold;
        color: #FF4B4B;
        padding: 10px 0;
        margin: 20px 0;
    }
    </style>
    <div class="annotation-header">📝 选择标注模式</div>
    """, unsafe_allow_html=True)
    
    # 标注模式选择
    annotation_mode = st.radio(
        "",  # 移除标签文字，因为已经用上面的标题替代
        ["词语级标注（标注每个词的类别）", "句子级标注（标注整句的类别）"],
        key="annotation_mode_select"
    )
    
    st.markdown("---")  # 添加分隔线
    
    if annotation_mode == "词语级标注（标注每个词的类别）":
        # 标注类型选择
        st.markdown('<div style="font-size: 1.2em; font-weight: bold; color: #333;">选择标注类型：</div>', 
                   unsafe_allow_html=True)
        label_type = st.radio(
            "",  # 移除标签文字
            ["命名实体", "词性", "语义角色", "自定义标注"],
            key="label_type_select"
        )
        
        # 根据不同的标注类型提供不同的默认标签
        if label_type == "命名实体":
            default_labels = "人名,地名,组织名,时间,数量,其他"
            help_text = "用于标注文本中的实体类型"
        elif label_type == "词性":
            default_labels = "名词,动词,形容词,副词,代词,介词,连词,助词,叹词,数词,量词,其他"
            help_text = "用于标注词语的词性类别"
        elif label_type == "语义角色":
            default_labels = "施事,受事,与事,工具,处所,时间,方式,原因,目的,结果,其他"
            help_text = "用于标注词语在句子中的语义角色"
        else:  # 自定义标注
            default_labels = "标签1,标签2,标签3"
            help_text = "请输入您自定义的标注类别，用逗号分隔"
            
            # 自定义标注名称
            custom_annotation_name = st.text_input(
                "输入标注任务名称（例如：情感倾向、主题分类等）：",
                value="自定义标注任务",
                key="custom_annotation_name"
            )
            st.write(f"当前标注任务：{custom_annotation_name}")
        
        # 自定义标签
        st.write(f"设置{label_type}标注的类别")
        custom_labels = st.text_input(
            "输入标注类别（用逗号分隔）：",
            value=default_labels,
            help=help_text,
            key="annotation_custom_labels"
        ).split(',')
        
        # 显示标注说明
        with st.expander("查看标注说明"):
            if label_type == "命名实体":
                st.markdown("""
                - 人名：人物的姓名
                - 地名：地理位置名称
                - 组织名：公司、机构、组织等名称
                - 时间：时间词语
                - 数量：数量词语
                - 其他：其他类型的实体
                """)
            elif label_type == "词性":
                st.markdown("""
                - 名词：表示人、事物、概念等
                - 动词：表示动作、行为、变化等
                - 形容词：表示性质、状态等
                - 副词：修饰动词、形容词等
                - 代词：代替名词、数词等
                - 介词：表示关系的虚词
                - 连词：连接词语、句子的虚词
                - 助词：辅助表达的虚词
                - 叹词：表示感叹语气
                - 数词：表示数量
                - 量词：表示单位
                - 其他：其他词性
                """)
            elif label_type == "语义角色":
                st.markdown("""
                - 施事：动作的执行者
                - 受事：动作的承受者
                - 与事：动作涉及的其他对象
                - 工具：动作使用的工具
                - 处所：动作发生的地点
                - 时间：动作发生的时间
                - 方式：动作的方式
                - 原因：动作的原因
                - 目的：动作的目的
                - 结果：动作的结果
                - 其他：其他语义角色
                """)
            else:  # 自定义标注说明
                st.markdown("""
                ### 自定义标注说明
                1. 在上方输入您的标注任务名称
                2. 在标注类别中输入您需要的标签，用逗号分隔
                3. 建议添加"其他"类别以处理特殊情况
                4. 标签名称建议简洁明确
                5. 可以在下方添加您的标注规则说明
                """)
                
                # 允许用户添加自定义说明
                custom_guidelines = st.text_area(
                    "添加您的标注规则说明（可选）：",
                    value="",
                    height=100,
                    key="custom_guidelines"
                )
                if custom_guidelines:
                    st.markdown("### 自定义标注规则")
                    st.markdown(custom_guidelines)
        
        # 初始化标注结果
        if 'annotations' not in st.session_state:
            st.session_state.annotations = {}
        
        # 显示标注界面
        st.write("### 词语标注")
        for i, sentence in enumerate(sentences):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"句子 {i+1}: {sentence}")
            with col2:
                # 改进的英文分词处理
                def split_english_words(text):
                    # 处理驼峰命名
                    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
                    # 处理连续的大写字母（如AI、GPU）
                    text = re.sub(r'([A-Z])([A-Z][a-z])', r'\1 \2', text)
                    # 处理数字和字母的组合
                    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
                    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
                    return text

                # 先处理英文
                processed_sentence = split_english_words(sentence)
                
                # 分词处理
                words = []
                # 使用正则表达式找出所有英文单词和其他字符
                pattern = r'[A-Za-z]+|[\u4e00-\u9fff]+'
                matches = re.finditer(pattern, processed_sentence)
                
                for match in matches:
                    word = match.group()
                    if re.match(r'^[A-Za-z]+$', word):  # 英文单词
                        words.append(word)
                    else:  # 中文字符
                        words.extend(jieba.lcut(word))
                
                # 标注处理
                annotations = []
                for j, word in enumerate(words):
                    if word.strip():  # 只标注非空词语
                        unique_key = f"annotation_seq_{i}_{j}_{word}"
                        label = st.selectbox(
                            f"'{word}' 的类别",
                            ["无标注"] + custom_labels,
                            key=unique_key
                        )
                        annotations.append((word, label))
                st.session_state.annotations[i] = annotations
                
    else:  # 句子级标注
        # 自定义类别
        st.write("设置句子标注的类别，例如：积极、消极、中性等")
        custom_categories = st.text_input(
            "输入标注类别（用逗号分隔）：",
            value="积极,消极,中性",
            help="这些类别将用于标注整个句子的属性",
            key="annotation_custom_categories"
        ).split(',')
        
        # 初始化分类结果
        if 'classifications' not in st.session_state:
            st.session_state.classifications = {}
            
        # 显示分类界面
        st.write("### 句子标注")
        for i, sentence in enumerate(sentences):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"句子 {i+1}: {sentence}")
            with col2:
                category = st.selectbox(
                    "选择句子类别",
                    custom_categories,
                    key=f"annotation_cat_{i}"
                )
                st.session_state.classifications[i] = {
                    'text': sentence,
                    'category': category
                }
    
    # 导出标注结果
    if st.button('导出标注结果', key='annotation_export'):
        if annotation_mode == "词语级标注（标注每个词的类别）":
            # 收集所有标注结果
            results = []
            for sent_id, annotations in st.session_state.annotations.items():
                for word, label in annotations:
                    if label != "无标注":  # 只收集已标注的词
                        results.append({
                            'sentence_id': sent_id + 1,
                            'word': word,
                            'label': label
                        })
            
            # 创建完整数据和已标注数据的DataFrame
            df_all = pd.DataFrame([
                {
                    'sentence_id': sent_id + 1,
                    'word': word,
                    'label': label
                }
                for sent_id, annotations in st.session_state.annotations.items()
                for word, label in annotations
            ])
            
            df_labeled = pd.DataFrame(results)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 导出全部数据
                if not df_all.empty:
                    csv_all = df_all.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="下载全部标注数据(CSV)",
                        data=csv_all,
                        file_name="annotations_all.csv",
                        mime="text/csv",
                        help="包含所有词语的标注结果，包括未标注的词"
                    )
            
            with col2:
                # 导出已标注数据
                if not df_labeled.empty:
                    csv_labeled = df_labeled.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="下载已标注数据(CSV)",
                        data=csv_labeled,
                        file_name="annotations_labeled.csv",
                        mime="text/csv",
                        help="只包含已标注的词语（不包含"无标注"的词）"
                    )
            
            # 显示标注统计信息
            st.info(f"""
            📊 标注统计：
            - 总词数：{len(df_all)}
            - 已标注词数：{len(df_labeled)}
            - 标注率：{(len(df_labeled)/len(df_all)*100):.1f}%
            """)
            
            # 同样提供JSON格式
            col3, col4 = st.columns(2)
            
            with col3:
                if not df_all.empty:
                    json_str_all = df_all.to_json(orient='records', force_ascii=False, indent=2)
                    st.download_button(
                        label="下载全部标注数据(JSON)",
                        data=json_str_all.encode('utf-8'),
                        file_name="annotations_all.json",
                        mime="application/json"
                    )
            
            with col4:
                if not df_labeled.empty:
                    json_str_labeled = df_labeled.to_json(orient='records', force_ascii=False, indent=2)
                    st.download_button(
                        label="下载已标注数据(JSON)",
                        data=json_str_labeled.encode('utf-8'),
                        file_name="annotations_labeled.json",
                        mime="application/json"
                    )

def export_danmu_analysis(df, video_title):
    """
    导出弹幕分析结果为CSV文件
    
    Args:
        df: 包含弹幕分析结果的DataFrame
        video_title: 视频标题，用于文件命名
    """
    try:
        # 生成文件名（移除不合法的文件名字符）
        safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
        filename = f"{safe_title}_弹幕分析.csv"
        
        # 转换为CSV并编码
        csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        
        # 提供下载按钮
        st.download_button(
            label="📥 下载弹幕分析结果",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            help="下载完整的弹幕分析数据"
        )
        
    except Exception as e:
        st.error(f"导出文件时发生错误: {str(e)}")
