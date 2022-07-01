# Rich Media

Datapane allows you to include many different types of content in your report, such as code, LaTeX formulas, images, embeds, HTML and more. See an example below:&#x20;

```python
import datapane as dp

html = """
<html>
    <style type='text/css'>
        @keyframes example {
            0%   {color: #EEE;}
            25%  {color: #EC4899;}
            50%  {color: #8B5CF6;}
            100% {color: #EF4444;}
        }
        #container {
            background: #1F2937;
            padding: 10em;
        }
        h1 {
            color:#eee;
            animation-name: example;
            animation-duration: 4s;
            animation-iteration-count: infinite;
        }
    </style>
    <div id="container">
      <h1> Welcome to my Report </h1>
    </div>
</html>
"""

obj_dict = {
  "brand": "Ford",
  "model": "Mustang",
  "year": 1964
}

report = dp.Report(
    dp.Text("""
## Example report with rich media
"""),
    dp.Formula("x^2 + y^2 = z^2"),
    dp.Code("""
# This is a snippet of Python code
def hello_world():
    print("Hello world")
    
hello_world()
    """),
    dp.HTML(html),
    dp.Embed(url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'),
    dp.File(obj_dict, is_json=True)
)

report.upload(name="Rich Media")
```

Running that code generates the following report:&#x20;

{% embed url="https://datapane.com/u/johnmicahreid/reports/aAMZ2G3/rich-media/embed" %}



