# Styling

Keen to mix up your report? You can change the font, background colour and text alignment to match your brand guidelines or personal aesthetics. There are two methods for doing this: via the API, and via the Report Settings page.&#x20;

{% hint style="info" %}
This feature is available for Datapane version 0.11.11 or later
{% endhint %}

## Python API

When you create a report, you can **** override the default styling properties by passing in a `ReportFormatting` object as follows:&#x20;

```python
dp.Report(
    ...
).upload(
    name="test_report",
    formatting=dp.ReportFormatting(
        light_prose=False, 
        accent_color="orange", 
        bg_color="#EEE", 
        text_alignment=dp.TextAlignment.RIGHT,
        font=dp.FontChoice.MONOSPACE
        width=dp.ReportWidth.MEDIUM
    )
)
```

There are currently six styling properties supported:&#x20;

**1.Light Prose**

Boolean which controls whether the text appears as light (good for dark mode), or dark (default).&#x20;

**2. Accent Colour**

Controls the colour of certain UI elements e.g. page titles, selects, DataTable headings. Can be any of the [140 CSS colour names](https://htmlcolorcodes.com/color-names/) or an RGB hex code. &#x20;

**3. Background Colour**

Controls the background colour of the page.  Can be any of the [140 CSS colour names](https://htmlcolorcodes.com/color-names/) or an RGB hex code. &#x20;

**4. Text Alignment**

Controls how the text is aligned - can be any of `JUSTIFY`, `LEFT` (default),   `RIGHT`, `CENTER`.&#x20;

**5. Font**

Controls the font for the prose text - can be any of `DEFAULT`, `SANS`, `SERIF`, `MONOSPACE`.&#x20;

6\. **Width**&#x20;

Controls the horizontal width of the report - can be any of `NARROW`, `MEDIUM` (default), `FULL`.&#x20;

## Report Settings Page

You can also edit these properties through the Visual Settings section of the Report Settings page.&#x20;

![](../../.gitbook/assets/screenshot-2021-07-26-at-11.28.53.png)

You'll see a CSS block here, where you can edit the default values. The same options apply as specified for the Python API above.&#x20;

```css
:root {
    --dp-accent-color: #4E46E5;
    --dp-bg-color: #FFF;
    --dp-text-align: justify;
    --dp-font-family: Inter var, ui-sans-serif, system-ui;
}
```

{% hint style="info" %}
**Datapane Teams** users have additional functionality for loading in custom fonts and header images into a global styling block that applies to all reports. To learn more, check out the section on [Styling and Whitelabelling](../../datapane-teams/styling.md).&#x20;
{% endhint %}
