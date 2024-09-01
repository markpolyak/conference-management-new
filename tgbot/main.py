import json
import requests as rq
import pytz
import datetime

from db import operations as db
from gdrive import operations as gdrive

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackContext,
    filters
)

from config.setup import setup
from utils.conversations import ValuePasser
from docx_builders import docx_builders


TGCONFIG = setup('telegram bot')
BACKEND_ENDPOINT = setup('backend')
DB_CONF = setup('database')
DRIVE_CONF = setup('google drive')

UPDATE_ID = ValuePasser()


async def start(update, context):
    uid = update.message.chat.id
    uname = update.message.chat.first_name
    if db.verify_user(DB_CONF, uid):
        await update.message.reply_text('You are already registered')
        return

    db.add_user(DB_CONF, uid, uname)


async def get_conferences(update, context):
    uid = update.message.chat.id
    if not db.verify_user(DB_CONF, uid):
        await update.message.reply_text('Not registered, run /start')
        return

    args = context.args
    if len(args) > 1:
        await update.message.reply_text('You can\'t specify more than one filter')
        return

    filter = 'active'
    if len(args) == 1:
        filter = args[0]

    try:
        params = {'filter': filter}
        resp = rq.get(BACKEND_ENDPOINT.get_uri, params=params, timeout=5)
        if resp.status_code != 200:
            raise Exception('Could not fetch data')

        pretty_json = json.dumps(resp.json(), ensure_ascii=False, indent=4)
        await update.message.reply_text(pretty_json)

    except Exception as e:
        print(e)
        await update.message.reply_text('Could not fetch data')


async def add_conference(update, context):
    uid = update.message.chat.id
    if not db.verify_user(DB_CONF, uid):
        await update.message.reply_text('Not registered, run /start')
        return ConversationHandler.END

    await update.message.reply_text("""
Adding new conference entry  
Specify data as following e g :  
```
{
    "google_spreadsheet": "example",
    "google_drive_directory_id": "example",
    "name_rus": "name",
    "name_rus_short": "short name",
    "registration_start_date": "01.08.2024",
    "registration_end_date": "01.10.2024",
    "submission_start_date": "01.08.2024",
    "submission_end_date": "01.10.2024",
    "conf_start_date": "01.10.2024",
    "conf_end_date": "10.10.2024",
    "organized_by": "SUAI",
    "url": "https://suai.com",
    "email": "suai@gmail.com"
}
```
""", parse_mode='MarkdownV2')
    return 0


async def backend_post(update, _):
    user_input = update.message.text
    if not user_input:
        return ConversationHandler.END

    await update.message.reply_text('Processing...')

    try:
        resp = rq.post(BACKEND_ENDPOINT.post_uri, data=user_input, timeout=5)
        if resp.status_code != 201:
            await update.message.reply_text('Invalid data submitted, check your input')
            raise Exception(f'Error: status code {resp.status_code}')

        await update.message.reply_text('Successfully added')

    except Exception as e:
        print(e)

    finally:
        return ConversationHandler.END


async def update_conference(update, context):
    uid = update.message.chat.id
    if not db.verify_user(DB_CONF, uid):
        await update.message.reply_text('Not registered, run /start')
        return ConversationHandler.END

    args = context.args
    if len(args) != 1:
        await update.message.reply_text('You need to specify id of the conference you want to update')
        return ConversationHandler.END

    try:
        UPDATE_ID.value = args[0]
    except Exception as e:
        await update.message.reply_text(f'Specified conference id must be an int > 0\nFull error: {e}')
        return ConversationHandler.END

    await update.message.reply_text("""
Adding new conference entry  
Specify data as following e g :  
```
{
    "google_spreadsheet": "example",
    "google_drive_directory_id": "example",
    "name_rus": "name",
    "name_rus_short": "short name",
    "registration_start_date": "01.08.2024",
    "registration_end_date": "01.10.2024",
    "submission_start_date": "01.08.2024",
    "submission_end_date": "01.10.2024",
    "conf_start_date": "01.10.2024",
    "conf_end_date": "10.10.2024",
    "organized_by": "SUAI",
    "url": "https://suai.com",
    "email": "suai@gmail.com"
}
```
""", parse_mode='MarkdownV2')
    return 0


async def backend_put(update, context):
    user_input = update.message.text
    if not user_input:
        return ConversationHandler.END

    await update.message.reply_text('Processing...')

    try:
        resp = rq.put(f'{BACKEND_ENDPOINT.put_uri}{UPDATE_ID.value}', data=user_input, timeout=5)
        if resp.status_code != 200:
            await update.message.reply_text('Invalid data submitted, check your input')
            raise Exception(f'Error: status code {resp.status_code}')

        await update.message.reply_text(f'Successfully updated record with id {UPDATE_ID.value}')

    except Exception as e:
        print(e)

    finally:
        return ConversationHandler.END


async def get_conference_applications(update, context):
    uid = update.message.chat.id
    if not db.verify_user(DB_CONF, uid):
        await update.message.reply_text('Not registered, run /start')
        return 

    args = context.args
    if len(args) != 1:
        await update.message.reply_text('You need to specify id of the conference')
        return 

    conference_id = args[0]
    if not conference_id.isdigit():
        await update.message.reply_text(f'Specified conference id must be an int > 0')
        return

    await update.message.reply_text('Processing...')

    try:
        resp = rq.get(f'{BACKEND_ENDPOINT.get_single_uri}{conference_id}')
        if resp.status_code != 200:
            raise Exception('Could not fetch data from backend')

        js_resp = resp.json()
        if not js_resp:
            raise Exception('Got null response from backend')

    except Exception as e:
        await update.message.reply_text(f'{e}')
        return

    drive_dir_id = js_resp.get('google_drive_directory_id')
    if not drive_dir_id:
        await update.message.reply_text('Current conference does not have drive directory set')
        return

    files = gdrive.get_folder_files(DRIVE_CONF, drive_dir_id, 'Applications')
    if not files:
        await update.message.reply_text('Could not fetch files from Applications folder')
        return

    msg_text = ''
    for i, f in enumerate(files):
        msg_text += f"File {i+1}:\nName: {f.get('name')}\nLink: {f.get('webViewLink')}\n\n"

    if not msg_text:
        await update.message.reply_text('No files were found')
        return

    await update.message.reply_text(msg_text)


async def get_conference_submissions(update, context):
    uid = update.message.chat.id
    if not db.verify_user(DB_CONF, uid):
        await update.message.reply_text('Not registered, run /start')
        return 

    args = context.args
    if len(args) != 1:
        await update.message.reply_text('You need to specify id of the conference')
        return 

    conference_id = args[0]
    if not conference_id.isdigit():
        await update.message.reply_text(f'Specified conference id must be an int > 0')
        return

    await update.message.reply_text('Processing...')

    try:
        resp = rq.get(f'{BACKEND_ENDPOINT.get_single_uri}{conference_id}')
        if resp.status_code != 200:
            raise Exception('Could not fetch data from backend')

        js_resp = resp.json()
        if not js_resp:
            raise Exception('Got null response from backend')

    except Exception as e:
        await update.message.reply_text(f'{e}')
        return

    drive_dir_id = js_resp.get('google_drive_directory_id')
    if not drive_dir_id:
        await update.message.reply_text('Current conference does not have drive directory set')
        return

    files = gdrive.get_folder_files(DRIVE_CONF, drive_dir_id, 'Submissions')
    if not files:
        await update.message.reply_text('Could not fetch files from Submissions folder')
        return

    d = docx_builders.SingularReport().create(files, f'Conference{conference_id}SubmissionsReport.docx')

    await update.message.reply_document(d)


async def get_conference_report(update, context):
    uid = update.message.chat.id
    if not db.verify_user(DB_CONF, uid):
        await update.message.reply_text('Not registered, run /start')
        return 

    args = context.args
    if len(args) < 1:
        await update.message.reply_text('You need to specify id of the conference and type of report: submissions or applications')
        return 

    conference_id = args[0]
    if not conference_id.isdigit():
        await update.message.reply_text(f'Specified conference id must be an int > 0')
        return

    report_type = 'default'
    if len(args) == 2:
        report_type = args[1]

    report_builder_resolve = {
        'default': (docx_builders.ConferenceReport(), 'Report'),
        'submissions': (docx_builders.SingularReport(), 'Submissions'),
        'applications': (docx_builders.SingularReport(), 'Applications'),
    }

    doc_builder, files_folder = report_builder_resolve.get(report_type)
    if not all([doc_builder, files_folder]):
        await update.message.reply_text('Third argument can only be one of: submissions, applications or None')
        return
    
    await update.message.reply_text('Processing...')

    try:
        resp = rq.get(f'{BACKEND_ENDPOINT.get_single_uri}{conference_id}')
        if resp.status_code != 200:
            raise Exception('Could not fetch data from backend')

        js_resp = resp.json()
        if not js_resp:
            raise Exception('Got null response from backend')

    except Exception as e:
        await update.message.reply_text(f'{e}')
        return

    drive_dir_id = js_resp.get('google_drive_directory_id')
    if not drive_dir_id:
        await update.message.reply_text('Current conference does not have drive directory set')
        return

    if files_folder in ['Submissions', 'Applications']:
        folder_files = gdrive.get_folder_files(DRIVE_CONF, drive_dir_id, files_folder)
        if not folder_files:
            await update.message.reply_text(f'Could not fetch files from {files_folder} folder')
            return

        d = doc_builder.create(folder_files, f'Conference{conference_id}{files_folder}.docx')

        await update.message.reply_document(d)
    else:
        d = doc_builder.create(js_resp, f'Conference{conference_id}Report.docx')

        await update.message.reply_document(d)


async def notificate_users(context: CallbackContext):
    """
    Check if any conferences are active today and notificate users
    """
    user_ids = db.get_all_users(DB_CONF)

    # get today's conferences
    try:
        params = {'filter': 'active'}
        resp = rq.get(BACKEND_ENDPOINT.get_uri, params=params, timeout=5)
        if resp.status_code != 200:
            raise Exception('Could not fetch data')

        # pretty_json = json.dumps(resp.json(), ensure_ascii=False, indent=4)
        # print(pretty_json)
        # await update.message.reply_text(pretty_json)
    except Exception as e:
        print(e)
        return 

    conf_list = ""
    for conf in resp.json():
        conf_list += f'id: {conf.get("id")}\n'
        conf_list += f'Short name: {conf.get("name_rus_short")}\n'
        conf_list += f'Started at: {conf.get("conf_start_date")}\n'
        conf_list += f'Ends at: {conf.get("conf_end_date")}\n\n'

    msg = f"""
Hello, today we have {len(resp.json())} active conferences:
{conf_list}
"""

    for uid in user_ids:
        await context.bot.send_message(chat_id=uid, text=msg)



async def cancel(update, _):
    await update.message.replly_text('cancelled')
    return ConversationHandler.END


async def help(update, _):
    help_message = """
/start
/get [<filter>] - get conferences with filter[active,future,past], default - active
/add
/update <id> - update conference, specify id of the conference
/applications <id> - get a list of applications to a specific conference, specify id of the conference
/submissions <id> - get a docx file with a list of submissions to a specific conference, specify id of the conference
/report <id>, [applications/submissions] - get a docx file with applications/submissions/everything about a specific conference, default type - everything
    """
    await update.message.reply_text(help_message)


def main():
    try:
        app = Application.builder().token(TGCONFIG.token).build()
    except Exception as e:
        print(f'Could not startup the application: {e}')
        exit(1)

    add_conference_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', add_conference)],
        states={
            0: [
                MessageHandler(
                    filters.ALL,
                    backend_post,
                )
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    update_conference_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('update', update_conference)],
        states={
            0: [
                MessageHandler(
                    filters.ALL,
                    backend_put,
                )
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('get', get_conferences))
    app.add_handler(CommandHandler('applications', get_conference_applications))
    app.add_handler(CommandHandler('submissions', get_conference_submissions))
    app.add_handler(CommandHandler('report', get_conference_report))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(add_conference_conv_handler)
    app.add_handler(update_conference_conv_handler)

    app.job_queue.run_daily(
        callback=notificate_users,
        time=datetime.time(
            hour=8,
            minute=00,
            second=00,
            tzinfo=pytz.timezone('Europe/Moscow')
        ),
        days=(0, 1, 2, 3, 4, 5, 6)
    )

    app.run_polling()


if __name__ == '__main__':
    print('Application started')
    main()
