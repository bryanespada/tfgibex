#!/bin/sh

#rm -rf .git
#rm -f .gitignore

python3 manage.py makemigrations &&
python3 manage.py migrate &&
python3 manage.py collectstatic --noinput &&

# # Generate a default admin superuser
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('leroydeniz@gmail.com', 'leroydeniz@gmail.com', 'lolipopp')" | python3 manage.py shell &&
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('trabajo.jorge2000@gmail.com', 'trabajo.jorge2000@gmail.com', 'putita202')" | python3 manage.py shell &&

# # Generate the default configuration item
# echo "from appmodels.models import GeneralConfig; import os; GeneralConfig.objects.create(app_name='Easy Regional Block', app_syncopation='ERB', app_icon='fa-solid fa-angles-right', app_logs='1', app_url='https://app.tfgibex.com/', currency='USD', paypal_client_id=os.environ.get('PAYPAL_CLIENT_ID', ''), paypal_secret_key=os.environ.get('PAYPAL_SECRET_KEY', ''), paypal_account_email=os.environ.get('PAYPAL_ACCOUNT_EMAIL', ''), google_oauth_client_id=os.environ.get('GOOGLE_OAUTH_CLIENT_ID', ''), google_oauth_client_secret=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', ''), google_analytics_tag_id=os.environ.get('GOOGLE_ANALYTICS_TAG_ID', ''))" | python3 manage.py shell &&

# # Generate the products
# echo "from appmodels.models import Product; Product.objects.create(title='The first title', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ut velit dignissim, varius dui vel, sodales magna. Nam maximus nulla ut odio interdum sollicitudin. Maecenas aliquam auctor ante, in facilisis erat varius in.', price='45.00', interval_count='2', interval_unit='M', public=True, discount='0')" | python3 manage.py shell &&
# echo "from appmodels.models import Product; Product.objects.create(title='The second title', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ut velit dignissim, varius dui vel, sodales magna. Nam maximus nulla ut odio interdum sollicitudin. Maecenas aliquam auctor ante, in facilisis erat varius in.', price='25.00', interval_count='1', interval_unit='M', public=True, discount='30')" | python3 manage.py shell &&
# echo "from appmodels.models import Product; Product.objects.create(title='The third title', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ut velit dignissim, varius dui vel, sodales magna. Nam maximus nulla ut odio interdum sollicitudin. Maecenas aliquam auctor ante, in facilisis erat varius in.', price='150.00', interval_count='1', interval_unit='Y', public=True, discount='55')" | python3 manage.py shell &&

# # Generate a surgical area example 
# echo "from appmodels.models import SurgicalArea; SurgicalArea.objects.create(title='The title of Surgical Area 1', description='The description of Surgical Area 1')" | python3 manage.py shell &&

# # Generate the Administration group to admins
# echo "from django.contrib.auth.models import Group; Group.objects.create(name='Administration')" | python3 manage.py shell &&

# # Add superuser to Administration groups
# echo "from django.contrib.auth import get_user_model; from django.contrib.auth.models import Group; user = get_user_model().objects.get(username='leroydeniz@gmail.com'); group = Group.objects.get(name='Administration'); user.groups.add(group)" | python3 manage.py shell &&
# echo "from django.contrib.auth import get_user_model; from django.contrib.auth.models import Group; user = get_user_model().objects.get(username='trabajo.jorge2000@gmail.com'); group = Group.objects.get(name='Administration'); user.groups.add(group)" | python3 manage.py shell &&

python3 manage.py runserver 0.0.0.0:8000
