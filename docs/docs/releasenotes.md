# Release Notes

!!! hint "Want to know what's next?"

    Check out our [Product Roadmap](https://datapane.nolt.io/roadmap) to see what upcoming features we are considering and make a suggestion!

## **30 August 2022**

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.15.0 |
| Breaking changes | True   |

### :octicons-organization-24: Workspaces

![](img/releasenotes/cloud.png){ .docs-image }

We have launched **Workspaces** on Datapane Cloud.

Datapane Cloud is the best way to host and share your apps, dashboards, and apps.

With this release, Datapane Cloud users can now securely share reports with their team or clients by creating private Workspaces and Projects.

[Create a free Workspace](https://datapane.com/accounts/signup){ .md-button }

### :octicons-repo-template-24: Templates and Components Catalogs

<a src="/catalogs/blocks/table"><img class="docs-image" src="https://user-images.githubusercontent.com/15690380/183948469-c76fa50f-e0a2-438a-b13c-9e58d6071c1c.png"></a>

Starting from this release, we are providing a series of templates and components which lower the barrier to building something awesome using Datapane and Python. Check them out in our new [Catalog](catalogs/index.ipynb).

Our first templates include:

#### Classifier dashboard

A performance dashboard for classifiers. It can be used as a starting point for creating a Datapane app that highlights the performance of multiple classifiers on a dataset.

#### Social media dashboard

An engagement dashboard for social media. It can be used as a starting point for creating a Datapane app that highlights user engagement with social media channels.

#### Text-heavy report

A text-heavy app. It can be used as a starting point for creating a text-heavy Datapane app that starts off as a Jupyter Notebook.

### :octicons-code-square-24: Open-source Report Renderer

Prior to this release, our report renderer was a bundled and minified Javascript library which was not open to contributions. As part of porting our Report renderer from React to Vue.js, we've taken the step of open-sourcing the entire renderer, which you can check out [on GitHub](https://github.com/datapane/datapane/tree/master/projects/web-components/report).

### :octicons-bug-24: Other Bug Fixes and Improvements

-   Add Plotapi support to `dp.Plot`
-   Update our `hello-world` report
-   Add a `dp.Dropdown` block to reports
-   Add SQL support to `dp.DataTable` on local reports
-   `dp.Page` dropdown and `dp.BigNumber` fixes
-   New documentation site hosted on mkdocs
-   Add Datapane in 3 minutes video to README
-   Add bipartite to bool conversion
-   Update the Contributing Docs ready for Open Contributions
-   Removed `datapane signup`

---

## **03 April 2022**

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.14.0 |
| Breaking changes | True   |

### App File Upload

Allow Enterprise users to upload files to their apps as parameters.

### Project support

Enable project and sharing on Enterprise and Datapane.com

---

## **08 December 2021**

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.14.0 |
| Breaking changes | True   |

### Enterprise Renaming

In preparation for unifying our enterprise and public products, we're renaming and upgrading some of our core objects to make them easier to understand.

-   `Script` will be renamed `App`
-   `Blob` will be renamed `File`
-   The current `dp.File` block will be split into `dp.Media` and `dp.Attachment`
-   `Group` will be renamed `Project`
-   `Variables` will be combined with Docker images into a new `Environment` system

This is a **breaking change**, meaning that any new objects you create after the update will need to follow the new syntax. Your existing scripts/blobs/groups should continue to work.

### :octicons-bug-24: Other Bug Fixes and Improvements

-   Fixed a bug where we didn't show explanatory text for Report Notifications on Org
-   Fixed a bug where `dp.Blob.upload_file` gave an error for certain filetypes
-   Fixed a bug where nested groups didn't always display correctly in the embed view
-   Fixed a bug where table cells didn't display correctly on Safari browsers
-   Updated our report preview text to sound more professional
-   Added a Divider block (`dp.Divider`) for more layout control

---

## 21 September 2021

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.12.1 |
| Breaking changes | False  |

### API-first Signup

In keeping with our vision of being a developer-friendly API-first product, we're launching a new onboarding experience for local client users. After installing Datapane, you'll be prompted to run the following command:

```
datapane hello-world
```

This will run some Python code to generate a local HTML report which demonstrates how the product works. After viewing that local report, you can run the following command to create an account and get an API key for hosting reports:

```
datapane signup
```

### :octicons-bug-24: Other Bug Fixes and Improvements

-   Improved `dp.Table` default styling
-   Added a SQL query runner to `dp.DataTable` for more advanced filtering and calculation logic
-   Fixed a bug where thumbnails weren't being generated for new reports

---

## **25 August 2021**

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.12.1 |
| Breaking changes | True   |

-   `app.publish` is now called `app.upload`
-   `dp.Markdown` replaced with `dp.Text` for text content
-   `dp.Page` must use `title` parameter to set the page title, not `label`
-   Objects like `scripts`, `blobs` and `variables` now keep their original name instead of being converted to lowercase slugs, for instance `my variable` won't be renamed to`my_variable`. You may need to update any scripts to use the new names (or re-add variables / blobs with the older names).

### DataTable Improvements

-   Fixed encoding issue mismatch between `dp.Table` and `dp.DataTable`.
-   Allow column autosizing on double-click
-   You can now input uppercase strings in column filters
-   `ID` column is no longer added by default, instead row numbers will appear to the left of the first column
-   `Select` and `Date` column types added

### :octicons-bug-24: Other Bug Fixes and Improvements

-   `dp.Select` blocks are now searchable, so they work better with many options
-   Report URLs no longer break when you change the title
-   Report thumbnails are now shown correctly when the first asset is an image
-   Added a product feedback form in left sidebar of Datapane Home
-   Per-report styling is now available on Enterprise
-   Medium exports no longer require Publishing an app
-   Streamlined `Home` and `Gallery` pages
-   If you have added code to an app, it will now show in the embed view

---

## **27 July 2021**

| Property         | Values  |
| ---------------- | ------- |
| Python version   | 0.11.11 |
| Breaking changes | False   |

### Report Styling

We've had a ton of feedback from users wanting to create more custom reports. Now you can set a custom background color, font, and text alignment. Try it on the Report Settings page or through our Python library.

### :octicons-bug-24: Other Bug Fixes and Improvements

-   Fixed the error `DataTable: No objects to concatenate`
-   Fixed DataTable numeric column sorting
-   Fixed a broken docs link for TextReports
-   Removed some unnecessary extra padding on report embeds
-   Removed signup requirement for 'Request Workspace' form
-   Added Google, Github OAuth options on signup page
-   Added >, >=, <, <= DataTable column filter options
-   Added a Copy button to the Code block for viewers
-   Added a Text icon to TextReports for multi-column layouts
-   Added 'Previous Page', 'Next Page' to reports with multiple pages
-   Improved report comment email notification
-   Doubled the allowed document size
-   Doubled the limit on `dp.Select` option names
-   Support both Jinja v2 and v3

---

## 3 July 2021

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.11.9 |
| Breaking changes | False  |

### Report Styling & Whitelabelling on Datapane Enterprise

Now you can add your own fonts, colours, custom headers and more on your Datapane Enterprise reports. This is great for organizations who have brand guidelines to follow, or want to experiment with their own defaults

### :octicons-bug-24: Other Bug Fixes and Improvements

-   Decreased report font size and changed from dark grey to black
-   Changed default padding on reports
-   Added fullscreen viewing options for embeds
-   Show a more informative error message when signing up with an expired email link
-   Changed default report visibility to Unlisted

---

## **6 June 2021**

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.11.8 |
| Breaking changes | False  |

### Settings & User Management

Admins on Datapane Enterprise have a lot more control over their instance, as we've added several new Settings pages:

**Account**

-   View pricing plan
-   Customise report sharing timeout
-   Set company logo
-   Set company name
-   Set docker registry credentials

**Team Members**

-   Invite a user via email
-   Set user role (admin, editor, viewer)
-   Add new user to group
-   See list of pending invites

**Groups**

-   Create a group
-   Add existing user to group

### On-premise installation

Datapane Enterprise can now be installed in your own cloud environment (AWS or GCP). This is perfect for users with stricter security requirements who want to ensure that confidential data doesn't leave their system. We use docker-compose to ensure that you can get up and running within 15 minutes.

Read our [installation guide](https://github.com/datapane/datapane-onpremise) on Github for more.

### :octicons-bug-24: Other Bug Fixes and Improvements

-   Better report header design
-   See the report visibility (Public/Private) on the 'My Reports' page
-   DataTable component is now available for offline reports generated via `app.save`
-   Live support chat added to hosted Datapane Enterprise instances
-   Clearer signup process for Datapane Enterprise users
-   'More from user' section of an app no longer shows that same report
-   Fixed a bug with Bokeh where some report blocks would be repeated

---

## **23 May 2021**

| Property         | Values |
| ---------------- | ------ |
| Python version   | 0.11.4 |
| Breaking changes | False  |

### :octicons-bug-24: Other Bug Fixes and Improvements

-   LaTeX equations can now be added to your apps! Check out the [Formula](catalogs/blocks/formula.ipynb) block for more info.
-   Increased the maximum size of an app from 25MB to 100MB
-   Enterprise Scripts can now specify environment variables directly from their `datapane.yaml` file - these can be static value or user variables that are dynamically injected into your script e.g. DB parameters.
-   Datapane Enterprise users can now set their private report sharing timeout (previously this was fixed at 48 hours)
-   Sharing a private report link sometimes broke due to an extra # being appended to the URL
