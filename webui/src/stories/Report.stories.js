import Report from "../components/Report.vue";

const REPORT_PROPS = {
    htmlHeader: `<style>:root {
    --dp-accent-color: #4E46E5;
    --dp-bg-color: #FFF;
    --dp-text-align: justify;
    --dp-font-family: Inter var, ui-sans-serif, system-ui;
}</style>`,
    report: {
        width: "medium",
        /* eslint-disable-next-line @typescript-eslint/camelcase */
        is_light_prose: false,
        document: `<Report version="1"><Internal/><Pages layout="side"><Page label="Intro"><Group columns="1"><Text><![CDATA[This page describes Datapane, an API for creating data-driven reports from Python.
Datapane reports are comprised of blocks, which can be collected together and laid-out to form multiple-pages reports.
Some of the basic blocks include tables and plots.

## Tables

The Table block displays a tabular set of data, and takes either a dataframe or a pandas Styler "styled" object,

\`\`\`python
dp.Table(df, caption="A Table")
\`\`\`]]></Text><Table src="/media/dp/cas/40/89/40893f523e75e835e65978c917b87967656f7e90fa018e5d1f33bfbaf7766b5e.tbl.html" caption="A table" type="application/vnd.datapane.table+html" size="848" uploaded_filename="" cas_ref="40893f523e75e835e65978c917b87967656f7e90fa018e5d1f33bfbaf7766b5e"/><Text><![CDATA[The DataTable block also takes a dataframe and allows the user to search and filter the data when viewing the report


## Plots

The Plot block supports Altair, Bokeh, Plotly, Matplotlib, and Folium plots,

\`\`\`python
dp.Plot(altair_plot, caption="A Plot")
\`\`\`]]></Text><Plot responsive="true" scale="1.0" src="/media/dp/cas/a2/e7/a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce.vl.json" type="application/vnd.vegalite.v4+json" size="4316" uploaded_filename="" cas_ref="a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce"/><Text><![CDATA[## Other Blocks

Datapane has many other block types, including formulas, files, embeds, images, and big numbers - see the Blocks page for more info.

Additionally layout blocks provide the ability nest blocks to create groups of columns and user selections - see the Layout page for more info.]]></Text><Group columns="0"><Media src="/media/dp/cas/e5/27/e52738c727831ae2f937c0567163aa59ec93f558535e7ba4432ba8a9c04b7479.png" type="image/png" size="6506" uploaded_filename="datapane-logo.png" cas_ref="e52738c727831ae2f937c0567163aa59ec93f558535e7ba4432ba8a9c04b7479"/><BigNumber heading="Datapane Blocks" value="11" prev_value="6" is_positive_intent="false" is_upward_change="true"/><Formula caption="Simple formula"><![CDATA[\\frac{1}{\\sqrt{x^2 + 1}}]]></Formula></Group></Group></Page><Page label="Layout"><Group columns="1"><Text><![CDATA[Blocks on a page can be laid-out in Datapane using a flexible row and column system. furthermore, multiple blocks can be
nested into a single block where the user can select between which block, e.g. a plot, to view.
See https://docs.datapane.com/reports/layout-and-customization for more info.

## Group Blocks

Group blocks allow you to take a list of blocks, and lay-them out over a number of \`rows\` and \`columns\`, allowing you to create 2-column layouts, grids, and more,

\`\`\`python
dp.Group(plot1, plot2, columns=2)
cells = [dp.Text(f"### Cell {x}") for x in range(6)]
dp.Group(*cells, columns=0)  # 0 implies auto
\`\`\`]]></Text><Group columns="2"><Plot responsive="true" scale="1.0" src="/media/dp/cas/f1/b6/f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010.vl.json" type="application/vnd.vegalite.v4+json" size="557" uploaded_filename="" cas_ref="f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010"/><Plot responsive="true" scale="1.0" src="/media/dp/cas/a2/e7/a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce.vl.json" type="application/vnd.vegalite.v4+json" size="4316" uploaded_filename="" cas_ref="a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce"/></Group><Group columns="3"><Text><![CDATA[### Cell 0]]></Text><Text><![CDATA[### Cell 1]]></Text><Text><![CDATA[### Cell 2]]></Text><Text><![CDATA[### Cell 3]]></Text><Text><![CDATA[### Cell 4]]></Text><Text><![CDATA[### Cell 5]]></Text></Group><Text><![CDATA[## Select Blocks

Select blocks allow you to collect a list of blocks, e.g. plots, and allow the user to select between them, either via tabs or a dropdown list.

\`\`\`python
dp.Select(plot1, plot2, type=dp.SelectType.TABS)
dp.Select(plot1, plot2, type=dp.SelectType.DROPDOWN)
\`\`\`]]></Text><Select type="tabs" name="vega_select"><Plot responsive="true" scale="1.0" src="/media/dp/cas/f1/b6/f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010.vl.json" type="application/vnd.vegalite.v4+json" size="557" uploaded_filename="" cas_ref="f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010"/><Plot responsive="true" scale="1.0" src="/media/dp/cas/a2/e7/a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce.vl.json" type="application/vnd.vegalite.v4+json" size="4316" uploaded_filename="" cas_ref="a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce"/></Select><Select type="dropdown"><Plot responsive="true" scale="1.0" src="/media/dp/cas/f1/b6/f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010.vl.json" type="application/vnd.vegalite.v4+json" size="557" uploaded_filename="" cas_ref="f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010"/><Plot responsive="true" scale="1.0" src="/media/dp/cas/a2/e7/a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce.vl.json" type="application/vnd.vegalite.v4+json" size="4316" uploaded_filename="" cas_ref="a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce"/></Select><Text><![CDATA[Both Group and Select blocks can be nested within one another, in any order to create, for instance dropdowns with 2 columns inside, as below

\`\`\`python
group1 = dp.Group(plot1, plot2, columns=2)
dp.Select(group1, df)
\`\`\`]]></Text><Select><Group columns="2"><Plot responsive="true" scale="1.0" src="/media/dp/cas/f1/b6/f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010.vl.json" type="application/vnd.vegalite.v4+json" size="557" uploaded_filename="" cas_ref="f1b6936a3d44cf1bc562c6eace8ea25e961a2452e9b607b437ea5ef0363c2010"/><Plot responsive="true" scale="1.0" src="/media/dp/cas/a2/e7/a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce.vl.json" type="application/vnd.vegalite.v4+json" size="4316" uploaded_filename="" cas_ref="a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce"/></Group><Table src="/media/dp/cas/8d/b0/8db09e0d2123980a837795fce94d2b3f2eac9abd28f0bfeb46c58fdcfcd2f3e1.tbl.html" type="application/vnd.datapane.table+html" size="847" uploaded_filename="" cas_ref="8db09e0d2123980a837795fce94d2b3f2eac9abd28f0bfeb46c58fdcfcd2f3e1"/></Select></Group></Page><Page label="Blocks"><Group columns="1"><Text><![CDATA[A list and demonstration of all the blocks supported by Datapane - see https://docs.datapane.com/reports/blocks for more info.

## Plot Blocks

\`\`\`python
dp.Group(dp.Plot(altair_plot, caption="Altair Plot"),
         dp.Plot(bokeh_plot, caption="Bokeh Plot"),
         dp.Plot(matplotlib_plot, caption="Matplotlib Plot"),
         dp.Plot(plotly_plot, caption="Plotly Plot"),
         dp.Plot(folium_plot, caption="Folium Plot"),
         columns=2)
\`\`\`]]></Text><Group columns="2" name="plots_group"><Plot responsive="true" scale="1.0" name="vega" src="/media/dp/cas/a2/e7/a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce.vl.json" caption="Altair Plot" type="application/vnd.vegalite.v4+json" size="4316" uploaded_filename="" cas_ref="a2e7a60c323176b57901e13e36c81ecc81988f1bc734abaa431718d8472becce"/><Plot responsive="true" scale="1.0" name="bokeh" src="/media/dp/cas/3c/f6/3cf6b0ba27c69c282e63773f8db815a951480d9fb89e7acb54510435f1f48a7c.bokeh.json" caption="Bokeh Plot" type="application/vnd.bokeh.show+json" size="3520" uploaded_filename="" cas_ref="3cf6b0ba27c69c282e63773f8db815a951480d9fb89e7acb54510435f1f48a7c"/><Plot responsive="true" scale="1.0" name="matplotlib" src="/media/dp/cas/51/fe/51fe1a5298dc859750f8df86644786b88acd1e9ff7434aa11423fafcafd40a25.svg" caption="Matplotlib Plot" type="image/svg+xml" size="11905" uploaded_filename="" cas_ref="51fe1a5298dc859750f8df86644786b88acd1e9ff7434aa11423fafcafd40a25"/><Plot responsive="true" scale="1.0" name="plotly" src="/media/dp/cas/e8/7c/e87cb05a1b69b3b89ff85ad381ab2688823641402a7a4fa2af41a76a40f970a9.pl.json" caption="Plotly Plot" type="application/vnd.plotly.v1+json" size="8077" uploaded_filename="" cas_ref="e87cb05a1b69b3b89ff85ad381ab2688823641402a7a4fa2af41a76a40f970a9"/><Plot responsive="true" scale="1.0" name="folium" src="/media/dp/cas/29/3c/293c4328278e954a59b30a9f04fde3d24c268554f992d8688355b649feef22e6.fl.html" caption="Folium Plot" type="application/vnd.folium+html" size="3212" uploaded_filename="" cas_ref="293c4328278e954a59b30a9f04fde3d24c268554f992d8688355b649feef22e6"/></Group><Text><![CDATA[## Table Blocks

\`\`\`python
dp.Table(df, caption="Basic Table")
dp.Table(styled_df, caption="Styled Table")
dp.DataTable(df, caption="Interactive DataTable")
\`\`\`]]></Text><Group columns="1"><Table name="table1" src="/media/dp/cas/2a/d4/2ad4efa585209e76123c7458a606aebe3a53caf60bde2048c785f7c6ae638d13.tbl.html" caption="Basic Table" type="application/vnd.datapane.table+html" size="1745" uploaded_filename="" cas_ref="2ad4efa585209e76123c7458a606aebe3a53caf60bde2048c785f7c6ae638d13"/><Table name="styled-table" src="/media/dp/cas/a8/b4/a8b4e3c91659eb5062c412f6417e96fc1677b65cdd7a4eb471db92bef81cf6b8.tbl.html" caption="Styled Table" type="application/vnd.datapane.table+html" size="4834" uploaded_filename="" cas_ref="a8b4e3c91659eb5062c412f6417e96fc1677b65cdd7a4eb471db92bef81cf6b8"/><DataTable name="data_table" src="/media/dp/cas/75/c0/75c0d17958291f5af7718823e85b25bfde248a3c0c7da2453d197b5d6c1ac142.arrow" caption="Interactive DataTable" type="application/vnd.apache.arrow+binary" size="14730" uploaded_filename="" cas_ref="75c0d17958291f5af7718823e85b25bfde248a3c0c7da2453d197b5d6c1ac142" rows="1000" columns="6" schema="[{&quot;name&quot;: &quot;A&quot;, &quot;metadata&quot;: null, &quot;field_name&quot;: &quot;A&quot;, &quot;numpy_type&quot;: &quot;UInt16&quot;, &quot;pandas_type&quot;: &quot;uint16&quot;}, {&quot;name&quot;: &quot;B&quot;, &quot;metadata&quot;: null, &quot;field_name&quot;: &quot;B&quot;, &quot;numpy_type&quot;: &quot;UInt16&quot;, &quot;pandas_type&quot;: &quot;uint16&quot;}, {&quot;name&quot;: &quot;C&quot;, &quot;metadata&quot;: null, &quot;field_name&quot;: &quot;C&quot;, &quot;numpy_type&quot;: &quot;UInt16&quot;, &quot;pandas_type&quot;: &quot;uint16&quot;}, {&quot;name&quot;: &quot;D&quot;, &quot;metadata&quot;: null, &quot;field_name&quot;: &quot;D&quot;, &quot;numpy_type&quot;: &quot;UInt16&quot;, &quot;pandas_type&quot;: &quot;uint16&quot;}, {&quot;name&quot;: &quot;E&quot;, &quot;metadata&quot;: null, &quot;field_name&quot;: &quot;E&quot;, &quot;numpy_type&quot;: &quot;UInt16&quot;, &quot;pandas_type&quot;: &quot;uint16&quot;}, {&quot;name&quot;: &quot;F&quot;, &quot;metadata&quot;: null, &quot;field_name&quot;: &quot;F&quot;, &quot;numpy_type&quot;: &quot;UInt16&quot;, &quot;pandas_type&quot;: &quot;uint16&quot;}]"/></Group><Text><![CDATA[## Text Blocks

\`\`\`python
dp.Text("Hello, __world__!")
dp.Code("print('Hello, world!')")
dp.Formula(r"\\frac{1}{\\sqrt{x^2 + 1}}")
dp.HTML("<h1>Hello World</h1>")
dp.BigNumber(heading="Datapane Blocks", value=11, prev_value=6, is_upward_change=True)
\`\`\`]]></Text><Group columns="0"><Text name="markdown"><![CDATA[Hello, __world__!]]></Text><Code language="python" name="code"><![CDATA[print('Hello, world!']]></Code><Formula><![CDATA[\\frac{1}{\\sqrt{x^2 + 1}}]]></Formula><HTML name="HTML"><![CDATA[<h1>Hello World</h1>]]></HTML><BigNumber heading="Datapane Blocks" value="11" prev_value="6" is_positive_intent="false" is_upward_change="true" name="big_num"/></Group><Text><![CDATA[## Embedding

You can embed any URLs that spport the OEmbed protocol, including YouTube and Twitter.

\`\`\`python
dp.Embed("https://www.youtube.com/watch?v=JDe14ulcfLA")
dp.Embed("https://twitter.com/datapaneapp/status/1300831345413890050")
\`\`\`]]></Text><Group columns="2"><Embed url="https://www.youtube.com/watch?v=JDe14ulcfLA" title="Datapane Quick Overview" provider_name="YouTube" name="youtube_embed"><![CDATA[<iframe width="720" height="540" src="https://www.youtube.com/embed/JDe14ulcfLA?feature=oembed" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>]]></Embed><Embed url="https://twitter.com/datapaneapp/status/1300831345413890050" title="https://twitter.com/datapaneapp/status/1300831345413890050" provider_name="Twitter"><![CDATA[<blockquote class="twitter-tweet" data-width="550"><p lang="en" dir="ltr">How to build an interactive Google Trends Report using Python <a href="https://t.co/D7H85h9ZZD">https://t.co/D7H85h9ZZD</a> <a href="https://twitter.com/hashtag/Python?src=hash&amp;ref_src=twsrc%5Etfw">#Python</a> <a href="https://twitter.com/hashtag/DataVisualization?src=hash&amp;ref_src=twsrc%5Etfw">#DataVisualization</a></p>&mdash; Datapane (@datapaneapp) <a href="https://twitter.com/datapaneapp/status/1300831345413890050?ref_src=twsrc%5Etfw">September 1, 2020</a></blockquote>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"><\\/script>]]></Embed></Group><Text><![CDATA[## Media and Attachments

Files and Python objects can be added to a Datapane report, and be viewed (depending on browser support) and downloaded.

\`\`\`python
dp.Media(file="./logo.png")
dp.Attachment(data=[1,2,3])
\`\`\`]]></Text><Group columns="2"><Media name="logo_img" src="/media/dp/cas/e5/27/e52738c727831ae2f937c0567163aa59ec93f558535e7ba4432ba8a9c04b7479.png" type="image/png" size="6506" uploaded_filename="datapane-logo.png" cas_ref="e52738c727831ae2f937c0567163aa59ec93f558535e7ba4432ba8a9c04b7479"/><Attachment filename="dp-tmp-567xak1k.pkl" src="/media/dp/cas/f9/34/f9343d7d7ec5c3d8bcced056c438fc9f1d3819e9ca3d42418a40857050e10e20.pkl" type="application/vnd.pickle+binary" size="22" uploaded_filename="" cas_ref="f9343d7d7ec5c3d8bcced056c438fc9f1d3819e9ca3d42418a40857050e10e20"/></Group></Group></Page></Pages></Report>`,
    },
};

export default {
    title: "Report",
    component: Report,
};

const Template = (args) => ({
    components: { Report },
    setup() {
        return { args };
    },
    /* eslint-disable-next-line quotes */
    template: '<report v-bind="args" />',
});

export const Demo = Template.bind({});
Demo.args = {
    reportProps: REPORT_PROPS,
};
