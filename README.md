# chat_project

## TODO (Unchecked)
- [ ] Update the prompts per research to cater for assessment and best practice found during roleplay discovery.
- [ ] Re skin functional pages to look pretty
- [ ] Add delete to the scenario and assignment management in teachers dashboard
- [ ] Create the admin dashboard for superusers to be able to edit users and change platform related features
- [ ] Admin page to allow editing of users and to enable teacher flag per user (admin only auth)
- [ ] User profile editor (email, bio, details, select free scenarios (one time?))
- [ ] Migrate to authentication via Google and other socials
  - [x] Google
  - [ ] Facebook
  - [ ] Snapchat
  - [ ] Others?
- [ ] Security assessment
- [ ] Accessability compliance
- [ ] LMS integration
- [ ] Screenshots and videos
- [ ] Socials campaign
- [ ] List potential use cases
  - [ ] Categories like "dealing with staff" and "talking to paitents"
- [ ] Integrate with paywall
- [ ] Marketing materials
- [ ] Landing page
  - [x] Structure
  - [x] Content
  - [ ] Mailing list
  - [x] Map
  - [x] Contact
  - [x] Rounded corers on cards?
- [ ] Payment gateway integration
- [ ] Content / curriculium upload and integration to prompt chain
- [ ] Implement redis in the EB environment
- [ ] Bold headings and indented lists in assessment feedback (prompt based or post process text?)
- [ ] TAFE skills inclusion of role play in any customer facing skills training
  - [ ] align with funding of skills gap

## TODO (Done)
- [x] Change signup and User model to email as username
- [x] Create and deploy to eb
- [x] Change to AJAX based updates for real time conversation with bot
- [x] Re do system prompt for best response based on latest chat-gpt models
- [x] New user select free scenarios page (3)
- [x] Launch landing page
- [x] Student dashboard accordian integration for each assignment
- [x] Teacher dashboard accordian integration for each student
- [x] 3 Free scenarios for individual freemium trial
- [x] Remaining pages to new look base.html integration
- [x] Update prompts from descriptions
- [x] Pallette based on landing page image. Teals and Browns
- [x] Set up end-to-end encryption through Load Balancer (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-endtoend.html)
 

##Notes
environment setup in ssh
source /var/app/venv/*/bin/activate
export $(/opt/elasticbeanstalk/bin/get-config --output YAML environment | 
         sed -r 's/: /=/' | xargs)
python3 manage.py migrate