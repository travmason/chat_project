# chat_project
 
## TODO
- [x] Change signup and User model to email as username
- [ ] Update the prompts per research to cater for assessment and best practice found during roleplay discovery.
- [x] Create and deploy to eb
- [x] Change to AJAX based updates for real time conversation with bot
- [ ] Re do system prompt for best response based on latest chat-gpt models
- [ ] Re skin functional pages to look pretty
- [ ] Admin page to allow editing of users and to enable teacher flag per user (admin only auth)
- [ ] User profile editor (email, bio, details, select free scenarios (one time?))
- [ ] New user select free scenarios page (3)
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
- [x] Launch landing page
- [ ] Payment gateway integration
- [x] Student dashboard accordian integration for each assignment
- [x] Teacher dashboard accordian integration for each student
- [ ] 3 Free scenarios for individual freemium trial
- [ ] Content / curriculium upload and integration to prompt chain
- [x] Remaining pages to new look base.html integration
- [ ] Bold headings and indented lists in assessment feedback (prompt based or post process text?)
- [ ] Update prompts from descriptions
- [x] Pallette based on landing page image. Teals and Browns
- [ ] TAFE skills inclusion of role play in any customer facing skills training
    - [ ] align with funding of skills gap
- [x] Set up end-to-end encryption through Load Balancer (https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-endtoend.html)

##Notes
environment setup in ssh
source /var/app/venv/*/bin/activate
export $(/opt/elasticbeanstalk/bin/get-config --output YAML environment | 
         sed -r 's/: /=/' | xargs)
python3 manage.py migrate