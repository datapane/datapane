# Authentication and Sharing

Datapane allows secure, authenticated sharing of reports, scripts, blobs, and secrets. Each user on your Datapane instance (e.g. https://acme.datapane.net) has a private password-protected account.

For information on installing the Datapane CLI and authenticating with your Datapane server, please see the relevant section of the [Getting Started](../../tut-getting-started.md#datapane-enterprise) guide.&#x20;

{% hint style="info" %}
Each Datapane instance exists as a separate database tenancy, so accounts are not shared between instances. You cannot use the same account to authenticate across multiple instances (including Datapane Community).
{% endhint %}

## Access Tokens

If you want to share a private report with an outside party - such as a client or contractor - you can use the link provided next to the **Share** button to generate a secure signed token. This link contains this token which allows anyone with the link to access the report, without signing up to Datapane.

![](<../../.gitbook/assets/Screenshot 2021-11-16 at 15.23.30.png>)

This token also works across embeds, so you can [embed](../../reports/publishing-and-sharing/embedding-reports/#business-tooling) a private report into platforms such as Confluence or your own webpage. You can also use the [report-notifications.md](../../reports/publishing-and-sharing/report-notifications.md "mention")mechanism for this.&#x20;

{% hint style="info" %}
For security reasons, access tokens are revoked after 48 hours, but this can be configured by your instance admin under Settings -> Account -> Secure signed link timeout.&#x20;
{% endhint %}

## Projects <a href="#projects" id="projects"></a>

To share a report with a specific group of people on your Datapane Server, your administrator can create a Project under Settings -> Projects. When a new user is added to your Datapane server, the administrator can add them to a specific project. This is especially useful for sharing with external clients.&#x20;

![](<../../.gitbook/assets/Screenshot 2021-11-16 at 15.16.50.png>)

{% hint style="warning" %}
Datapane Servers come with a default project. All reports and scripts are shared with the `default` group automatically. If you do not want specific internal or external users to view these reports, **do not add them to the `default` project**.
{% endhint %}

You can also change the project of a report via the web UI (as per the first image above).
