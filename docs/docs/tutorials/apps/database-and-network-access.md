# Integrating Databases or APIs

Unlike a traditional BI platform, Datapane does not offer a proprietary set of connectors for pulling data. Instead, you are free to use the Python ecosystem to connect to third-party platforms, such as your data warehouse, internal APIs, etc. This also enables the ability to pull and join data from multiple sources.&#x20;

When apps run on Datapane, they have full network access to allow you to connect out to other platforms.

{% hint style="info" %}
If you need to connect to an internal database and are using the cloud-hosted Datapane server product, please reach out to support if you need to whitelist your instance's IP address.
{% endhint %}

## Managing secrets&#x20;

If you are connecting to a third-party datastore, it may require a form of authentication. To make this flow easier, Datapane provides an Environments API. This enables you to securely store, share, and retrieve sensitive variables, as well as specify dependencies.

Please see the relevant documentation for more information on managing secrets.

{% content-ref url="variables.md" %}
[variables.md](variables.md)
{% endcontent-ref %}

## Managing SQL scripts

If you are connecting to a database or warehouse and need to include SQL files, you can package these up in your app deployment by copying them into your app's folder and [including them](configuration-and-dependencies.md#additional-files-and-folders) in your `datapane.yaml` .&#x20;

{% hint style="info" %}
Using a combination of Python and SQL opens up opportunities to use Python to template SQL based on input parameters, or dynamically generate database queries.&#x20;
{% endhint %}
