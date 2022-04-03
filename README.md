# ISYS20182: PPM Project Repository, 2022
Private code repository for PPM module at Nottingham Trent University for people in the Developer role (2022).

Where possible, **please attempt to do the following** to make things easier when determining work done amongst group members and to make the jobs of your peers in other roles easier:
- **Raise bugs and features to be implemented** as *Issues* 
- **When making new branches,** name them according to the **feature/change you are trying to implement.** The end program that will be presented is in the `main` branch, so make sure to **only merge changes to `main` when they have been checked to be stable** (i.e. don't actively work in that repository if you can help it.) 
- **If several of you are working on a related issue at once, you should commit changes to the same branch** (instead of having a separate branch for each of your changes and trying to merge them all into `main`). This helps reduce code conflicts and generally makes them easier to resolve.
- When you want to merge a branch into `main` (or another branch, depending), Github requires you to make a *pull request* with an associated title and description.
  - Your title should be a **simple description of the changes you have made** or the **issue you have addressed** (i.e. cleaned up `index.html`).
  - Your description should **summarize any changes you've made,** such that another developer can easily see what the pull request does.
    - Don't worry about making this *too* detailed, as all the changes can be reviewed by someone before accepting the request - it just saves time and lessens worries. All    developers will have the same ability to approve pull requests, so this is mostly a formality, but helps if for whatever reason you haven't the time to check things yourself (so somebody else can check your changes on your behalf).
    - Note that you can mention *issues* (https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue) in your pull requests, as well as other stuff (other pull requests, other branches). Github will typically give you some suggestions while writing to guide you with this.
<!-- Note: need to figure out a way to turn *issues* into the hyperlinked text instead of just having the link in brackets, since it's bad to read. -->

- Feel free to actively make documentation using the Wiki included in this repository; this will make it easier when having to make it for the actual coursework document, and makes it easier for peers to see how something works without having to trawl through code.

This `README` is by no means a final version; feel free to make changes if you think there is something else that needs to be added, or a way to mention things more cleanly. Since this file doesn't actually affect the program coursework itself either, committing straight to `main` isn't that bad (although it might cause conflicts for people who have branched the repository prior - in that case, just prioritise the newest version of `README`).

For the python code, install required dependencies in cmd using the following command:
- pip install flask flask_cors flask_sqlalchemy flask_login flask_bcrypt flask_wtf pyttsx3 wtforms
