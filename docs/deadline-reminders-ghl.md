# Deadline reminder emails (GHL setup)

The site side is built. Email reminders stay hidden until this is set up, so no
student is promised emails that aren't sent. The "Add to my calendar" button on
the Plan page already works without any of this.

## What the site sends

When a signed-in student turns on **Email me reminders** on the Plan page, the
site sends a GHL form submission (the same way as the counselling waitlist):

- Form name: `Deadline Reminders` (form id `deadline-reminders`)
- `email`: the student's email (GHL matches or creates the contact)
- `reminders_opt_in`: `yes` (or `no` when they turn it off)
- `deadline_1_date` … `deadline_5_date`: their next five deadlines, `YYYY-MM-DD`
- `deadline_1_label` … `deadline_5_label`: e.g. `Imperial College London: Submit your application — UCAS deadline (via UCAS)`

It's re-sent automatically whenever those next deadlines change (a deadline
passes, is ticked done, or a university is saved or removed).

## Set up in GHL

1. **Custom fields** (Settings → Custom Fields, Contact): create
   `deadline_1_date` … `deadline_5_date` as **Date** fields and
   `deadline_1_label` … `deadline_5_label` as **Single line** text, plus
   `reminders_opt_in` as **Single line**. Use exactly these keys.
2. **Send yourself a test.** In the code, set `EMAIL_REMINDERS_LIVE = true`
   (`evidapath-navigator/src/components/DeadlineReminders.tsx`), run the site
   locally, save a university, and turn reminders on. Open your contact in GHL:
   - If the custom fields are filled, go to step 3.
   - If the values only appear on the Activity timeline, add a workflow
     (trigger: *Form Submitted → Deadline Reminders*) with *Update Contact Field*
     actions that copy each submitted value into the matching custom field.
3. **Reminder workflow** for each `deadline_N_date` field: trigger *Custom Date
   Reminder* on that field, at 14, 3 and 1 day before, with the filter
   `reminders_opt_in` is `yes`. Action: send an email such as
   "{{contact.deadline_N_label}} is due on {{contact.deadline_N_date}}. Check the
   official page before you apply." and a button linking to the site's /plan page.
4. **Turn it on for everyone:** leave `EMAIL_REMINDERS_LIVE = true`, commit,
   and deploy as usual.

Include an unsubscribe link in the emails; turning the switch off on the Plan
page also sends `reminders_opt_in: no`.
