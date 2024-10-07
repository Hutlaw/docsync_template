# README: Sync Google Docs to GitHub

This repository allows you to automatically fetch the HTML of a Google Doc, modify it based on custom configurations (such as tab title, favicon, and alignment), and push the modified HTML to a specified location in a GitHub repository. It uses the Google Drive API to access the Google Docs content and GitHub Actions to automate the process. All formatting is done on Google Docs, allowing for easy formatting. You can keep this repository private and seperate from your site to keep your secrets secure too.

---

## Features
- Fetches HTML content from a Google Doc using the Google Drive API.
- Allows for easy customization of the tab title, favicon, and content alignment (left, center, or right).
- Automatically pushes the modified HTML to a specified location in the repository.
- Can be run manually or on a scheduled basis.

---

## Requirements

Before using this workflow, you need the following:
1. **Google Cloud Service Account**: With access to the Google Drive API to fetch your Google Docs content.
2. **GitHub Secrets**: To securely store your API keys and document details.

---

## Setup Guide

### Step 1: Create a Google Cloud Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Navigate to **APIs & Services > Library** and search for **Google Drive API**.
4. Enable the **Google Drive API** for your project.
5. Under **APIs & Services > Credentials**, click **Create Credentials** and select **Service Account**.
6. Follow the prompts to create your service account.
7. Once created, go to the **Keys** section and click **Add Key > Create New Key**. Select **JSON** format and download the file.
8. Open the JSON file and copy its contents — this will be added as a secret in GitHub.

### Step 2: Set Up GitHub Secrets

In your GitHub repository, go to **Settings > Secrets and variables > Actions**. Click **New repository secret** and add the following secrets:

- **`DID`**: This is the ID of your Google Doc. To find the document ID, open the Google Doc and check the URL. The document ID is the part between `/d/` and `/edit` in the URL.
  
  Example:  "https://docs.google.com/document/d/1abcdefgHIJKLMNOP1234/edit"
The document ID in this case is `1abcdefgHIJKLMNOP1234`.

- **`GCI`**: Your Google Client ID.

- **`GCS`**: Your Google Client Secret.

- **`GT`**: GitHub Token — this is automatically provided by GitHub Actions.

- **`Service_Account_Key`**: Paste the contents of the Google Cloud service account key JSON file here.

### Step 3: Edit `config.json`

The configuration for how the HTML content will be modified is controlled via the `config.json` file in your repository. You can edit this file to customize the following:

```json
{
"tab_title": "My Google Doc Page",   // The title to display on the browser tab
"favicon_url": "favicon.png",   // URL of the favicon to use
"html_alignment": "left",   // Alignment of the content on the page ('left', 'center', or 'right')
"github_html_path": "synced_docs/document.html"   // Where the HTML file will be saved in your GitHub repository
}
```
### Step 4: Run the action. 
Go to the actions tab
Click the button on the left labeled "Google Docs Sync to GitHub"
CLick Run Workflow
Run

Do note that in the YML code, it is preset to update automatically everyday. Feel free to edit that
