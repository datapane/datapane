# Managing Users

You can invite team members to your instance so your whole team has access to a shared environment for reports and scripts.&#x20;

{% hint style="info" %}
Datapane doesn't charge on a per-seat or per-user basis, so you can add as many people to your instance as you like!
{% endhint %}

### Inviting Users

If you're an Admin logging in to your instance for the first time, you'll be prompted to invite team members by email. You can also invite users later by going to Settings -> Manage Users. The invited user will receive an email with a secure signup link valid for 72 hours.&#x20;

![](../../.gitbook/assets/screenshot-2021-05-25-at-15.51.36.png)

### Roles and projects

Every user must be assigned to one of our three system roles:&#x20;

1. **Viewer** - can view reports and run scripts&#x20;
2. **Editor** - all permissions of viewer, plus creating reports and scripts
3. **Admin** - all permissions of editor, plus settings, user management and billing

The default project is automatically created by the server and is for internal users. If you need to invite an external collaborator for a specific report, see the section on [projects](./#projects).&#x20;

### Advanced

If you need to delete a user, click on the 'Advanced Settings' button next to the user's name. This will take you to the Django Admin Panel. We recommend unchecking the box under Permissions -> 'Active' instead of deleting the user permanently, as this will trigger a cascading deletion of all the objects and reports that user ever created.&#x20;

{% hint style="info" %}
Deactivated users won't be able to log into your instance, or upload any further reports and scripts.&#x20;
{% endhint %}
