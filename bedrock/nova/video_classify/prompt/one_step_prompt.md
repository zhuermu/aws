Understand the video content. Output 2 pieces of information: one is category, the other is tags. 

1. The category is a array of objects, and each object has three properties: catetory1, catetory2, and catetory3. catetory1 and catetory2 are string, and catetory3 is an array of strings. The weight property is a dictionary that maps each category to its corresponding weight. The weight is an integer between 0 and 100. The array length of category is 1 to 3. Based on your understanding of the video, output the number of categories in the array.

2. The tags are an array of objects, and each object has two properties: tag and scores. The tag is a string, and the scores is an integer between 0 and 100. The array length of tags is 1 to 5. 

### catetorys ###
"""
${catetorys}
"""

The output sample in the following JSON format:
{
    "catetorys": 
    [{
        "catetory1": "Economy & Business",
        "catetory2": "Companies & Enterprises",
        "catetory3": ["Corporate News & Events", "Startups & Investments"],
        "weight": {
            "Economy & Business": 75,
            "Companies & Enterprises": 70,
            "Corporate News & Events": 65,
            "Startups & Investments": 68
        }
    },
    {
        "catetory1": "Blockchain",
        "catetory2": "Cryptocurrencies",
        "catetory3": ["Bitcoin, Ethereum & Mainstream Coins", "Stablecoins & Emerging Tokens"],
        "weight": {
            "Blockchain": 80,
            "Cryptocurrencies": 75,
            "Bitcoin, Ethereum & Mainstream Coins": 70,
            "Stablecoins & Emerging Tokens": 68
        }
    }],
    "tags": [
        {
            "tag": "OKX",
            "scores": 100
        },
        {
            "tag": "DOGE",
            "scores": 90
        },
        {
            "tag": "Christmas",
            "scores": 80
        },
        {
            "tag": "family",
            "scores": 70
        },
        {
            "tag": "Santa Claus",
            "scores": 60
        },
        {
            "tag": "okxchinese",
            "scores": 40
        },
        {
            "tag": "OKXWallet",
            "scores": 30
        }
    ]
}

Remember that the classified information must be within the categories I provided. 
Please genarate on the json output, DO NOT provide any preamble.
