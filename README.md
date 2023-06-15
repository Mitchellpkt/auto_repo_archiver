# auto_repo_archiver

**!! Work in progress !!**

Given a keyword, 

(1) pulls down related [arXiv](https://arxiv.org/) papers 

(2) scans each page of each paper for [GitHub](https://github.com) repository URLs

(3) triggers the [Wayback Machine](https://archive.org/web/) to archive the repository, IF AND ONLY IF it has not already been archived

This is a hacky prototype, but I think the core functionality works. (note that at this time it only snapshots the repo homepage)

