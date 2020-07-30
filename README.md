# GitHub Issue Insights

### MSVan Hackathon 2020 Project
This repo contains code that was developed during Microsoft's Hackathon July 27-29 2020.

### [Link to product demo video](https://microsoft-my.sharepoint.com/:v:/p/sichitha/EXAGYzegCN9Npw-gIdrpjp0Bq7DdG7a_Dk8fbGmwE-l4cw?e=yum2zV)

### What does it do?
Issue Insights is a GitHub app that once installed on a repo, analyzes the code base and helps you find relevant info related to a new GitHub issue.
Once an issue is created on a repo that has Issue Insights installed, the app posts a comment on the issue with a recommendation of related pull requests, files and people to ask for more help. With this information from our Issue Insights App, you have valuable starting points to get started on your task right away!

### How did we build it?
Issue Insights is a python app that reads and writes to GitHub through the GitHub API. The app makes use of our recommender system which is an ML model we trained during the hackathon to find the most relevant information for new GitHub issues. Currently, the recommender will find the most relevant Pull Requests in the repo based on the information provided in the issue. We do some processing on those PRs to find the most relevant files and users who can help. 
Once we have this info, we post an issue comment through an API call. 

### How to run this?
More info about running the app can be found in [/app](https://github.com/alekhyareddy28/Github-Issue-Insights/tree/master/app)
