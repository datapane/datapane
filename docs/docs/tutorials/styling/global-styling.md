This section describes how to add custom colours and fonts to all the apps in your workspace.

## Styles

Datapane allows you to define a global style block which will apply to all of your apps. In this block you can \(re\)define the default font, background colour and more.

![Example of a styled app](../../img/tutorials/styling-whitelabelling-1.png)

To use this feature, you'll need to have Admin Access. Head over to Settings -&gt; Visual Settings, and scroll to the Styling section, where you'll see a block of HTML/CSS which looks like this:

```html
<style type="text/css">
    :root {
        --dp-accent-color: #fff;
        --dp-bg-color: #1f2937;
        --dp-text-align: justify;
        --dp-font-family: Inter var, ui-sans-serif, system-ui;
    }
</style>
```

You can edit this block to add your brand colors, load in a custom font or even add a logo. Any assets that you add will be displayed in a bar at the top of your app, and these changes will apply retroactively to your old apps.

### **Adding a custom font**

If you have a brand font, you can load it in as follows:

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Sofia" />

<style type="text/css">
    :root {
        --dp-accent-color: #fff;
        --dp-bg-color: #1f2937;
        --dp-text-align: justify;
        --dp-font-family: Sofia;
    }
</style>
```

Note that this will only apply to the headings and prose - UI text in DataTables, Select blocks etc will stay as the system default.

### **Adding a custom header**

Anything you add under the `<style>` block will be added to the top of your app as a default header. You can use this to load in a custom image, text or analytics script as follows:

```html
<style type="text/css">
    :root {
        --dp-accent-color: #4e46e5;
        --dp-bg-color: #fff;
        --dp-text-align: justify;
        --dp-font-family: Inter var, ui-sans-serif, system-ui;
    }
</style>

<img src="my-image.png" />
```
