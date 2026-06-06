# langchain-lead-gen

## objective
This is a sales lead generation agent that automates finding potential IT services customers in New Jersey.
Here's the flow:

Searches DuckDuckGo for small businesses in NJ that might need IT services
Scrapes their websites to gather details like contact info and emails
Analyzes the scraped content using GPT-4o-mini to build a structured profile for each business
Saves the results to a text file

The output for each lead is a structured object with the company name, contact info, email, a summary, a personalized outreach message, and which tools were used to find it — all driven by a LangChain ReAct agent that decides on its own which tools to call and in what order

### pre-req

```
# Create a fresh virtual environment with your 3.12
/PATH/TO/PYTHON3.12/python.exe -m venv venv

# Activate it
venv\Scripts\activate

# Confirm you're in the clean env
python --version

# Fresh install of everything
pip install -r requirements.txt
export OPENAI_API_KEY=XXXX

``` 

### execute 

```
python main.py
```


## expected output
```
{
  "leads": [
    {
      "company": "Departed Soles Brewing Co.",
      "contact_info": "(201) 479-8578",
      "email": "Not publicly available",
      "summary": "Jersey City's first modern brewery, offering a variety of craft beers including gluten-free options. They host events and have a tasting room open to the public.",
      "outreach_message": "Hi, I noticed your brewery has a great community presence. I believe enhancing your IT infrastructure could help streamline operations and improve customer engagement.",
      "tools_used": "Brewing equipment, POS systems, social media for marketing."
    },
    {
      "company": "Old Salt Gift Shop",
      "contact_info": "Not publicly available",
      "email": "Not publicly available",
      "summary": "Established in 1977, this coastal gift shop offers a wide selection of nautical and seashore-themed items. It caters to both locals and tourists, providing a charming shopping experience.",
      "outreach_message": "Hello, I admire your unique selection of coastal gifts. I think that optimizing your online presence and IT systems could enhance your customer experience and sales.",
      "tools_used": "Retail management systems, e-commerce platform, social media for promotions."
    }
  ]
}
```