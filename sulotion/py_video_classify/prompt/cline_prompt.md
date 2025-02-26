###项目首次初始化
```
### 实现一个视频分类程序，使用aws boto3 sdk 实现.

### 业务逻辑
开发一个视频分类工具，视频分类工具包含3个模块：
### 公共模块，用来提供公共的工具类和方法
1. 实现一个LLM调用方法，调用bedrock大模型，参数输入一个S3的视频URI 、 prompt 、 system 和 模型ID 等相关参数，输出打磨模型理解的结果， 调用 bedrock runtime 的converse 接口 的视频里面接口。
2. 实现一个视频准文本方法，视频转文本，参数输入一个 S3 的视频URI， 如果视频超过30秒，截取视频前30秒，返回视频里的音频文本，使用 amazon transcribe 服务实现，输入的视频语自动识别，支持中文、英文、日文、韩文等多种语言。
3. 实现一个分类结果校准方法，输入一、二、三级分类， 根据分类级别读取三级分类对象， 根据当前分类级，计算向量相似度最接近的一个词输出，使用amazon bedrock embedding 模型进行向量计算。如果分类不存在，则使用上一级分类进行向量计算。
4. 实现一个json结果解析方法，输入一段文本，从文本中提取json格式的数据，返回json格式的数据，如果json格式不正确，调用 nova lite 修复json格式。
   
### 视频分类模块
#### 一次视频分类模块，即一次性输入视频信息和prompt提示词信息，返回视频分类结果，功能如下：
1. 读取prompt文件，获取提示词，并设置LLM system 的人设为视频分类专家，用英语写，调用bedrock runtime 的converse 接口
2. 返回视频分类结果，调用json结果解析方法，解析json结果，返回json。
3. 调用分类结果校准方法，校准分类结果，返回校准结果。
4. 统计每次返回的token消耗量，分别input token 和 output token，返回token消耗量。
5. 将结果写入csv文件，csv文件的包括如下列：S3 URI、分类结果和标签结果、token消耗量。

### 视频评测模块
1. 读取视频分类好的结果文件，读取视频样本的真实分类结果，使用bedrock LLM 模型，调用bedrock runtime 的converse 接口，来计算准确率。

### 不同模型和方法的比较测试
#### 变量： 
1. 模型ID，Amazon Nova Pro 和 Amazon Nova Lite； 
2. 一步分类方法：直接输入Prompt 和 S3 URI，一次性返回分类结果和标签；
3. 两步分类方法：先输入Prompt 和 S3 URI，返回对视频内容的理解，再输入理解结果，返回分类结果和标签；
4、组合上面的变量，进行测试，比较不同模型和方法的准确率和速度。

### 视频预处理模块
写一个python脚本，读取video-input.csv 文件，的列media_info，下载文件并上传文件到S3 桶 video-classify 中。 截图视频文件大小，如果视频时间长度超过 30s，就截断后上传。

上传视频后，将视频的S3URI 和 分类、标签结果写入到csv文件中。
```

## 二次开发需求
```
### 优化代码：
1、加载分类从本地文件category.json读取；
2、组合prompt 时  prompt 里面的变量 ${catetorys} 也从category.json 读取组装；
3、oen step 和 two step 方法的prompt 都放在prompt 文件夹下，请从这里读取prompt 组合 category.json；
4、需要进行分类的数据从douyin_classification_data.csv 读取里面的s3地址，将生成的结果放在，douyin_classification_results.csv里面，保留越来的分类和标签数据方便对比。

### 继续优化代码：
1、使用step 类型和 model_id 两个参数生成的结果，命名不要重合，用于后面的数据评测，可以根据生成的不同文件名，来进行数据结果的准确性评测；
2、根据本次的修改完善README.md
```
