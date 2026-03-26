import pandas as pd

data = [
    ["ImageToBnW", "converts an image to black and white using PIL library", "['ImageProcessing','ComputerVision','PIL']", "['image_path']", "['path_to_image']"],
    ["CropImage", "crops image to specified ROI", "['ImageProcessing','ComputerVision','PIL']", "['image_path','roi_points']", "['path_to_processed_image']"],
    ["ResizeImage", "resizes image to target dimensions", "['ImageProcessing','ComputerVision']", "['image_path','width','height']", "['path_to_resized_image']"],
    ["DetectEdges", "performs Canny edge detection", "['ImageProcessing','ComputerVision','OpenCV']", "['image_path']", "['path_to_edge_image']"],
    ["BlendImages", "blends two images with adjustable alpha", "['ImageProcessing','ComputerVision','PIL']", "['image_path1','image_path2','alpha']", "['path_to_output_image']"],

    ["TokenizeText", "splits text into tokens", "['NLP','TextProcessing']", "['text']", "['tokens']"],
    ["POS_Tagger", "assigns part-of-speech tags", "['NLP','Linguistics']", "['tokens']", "['pos_tags']"],
    ["SentimentAnalysis", "predicts sentiment polarity", "['NLP','ML']", "['text']", "['sentiment_score']"],
    ["SummarizeText", "generates an extractive summary", "['NLP','Summarization']", "['text']", "['summary']"],
    ["TranslateText", "translates text to target language", "['NLP','MT']", "['text','target_lang']", "['translated_text']"],

    ["SortNumbers", "sorts numeric list", "['Math','Algorithms']", "['numbers']", "['sorted_numbers']"],
    ["MatrixMultiply", "multiplies two matrices", "['Math','LinearAlgebra']", "['matrix_a','matrix_b']", "['matrix_c']"],
    ["Fibonacci", "computes Fibonacci sequence up to N", "['Math','Sequences']", "['n']", "['fib_sequence']"],
    ["FourierTransform", "computes FFT", "['Math','SignalProcessing']", "['signal']", "['fft_output']"],
    ["SolveEquation", "solves algebraic equations", "['Math','Symbolic']", "['equation']", "['solution']"],

    ["ConnectToDB", "connects to database", "['Systems','Database']", "['connection_string']", "['connection_object']"],
    ["RunSQLQuery", "executes SQL query", "['Systems','Database']", "['connection','query']", "['result_set']"],
    ["ReadConfig", "reads configuration file", "['Systems','Config']", "['config_path']", "['config_dict']"],
    ["LogEvent", "logs an event to system logs", "['Systems','Logging']", "['event']", "['log_id']"],
    ["PingServer", "pings server and returns latency", "['Systems','Networking']", "['server_address']", "['latency_ms']"],
]

df = pd.DataFrame(data, columns=["name","description","tag","input_arguments","output"])

csv_path = ("./mock_data/blocks.csv")
df.to_csv(csv_path, index=False)

