// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.application_requirement) by
// 05-sanity/generation/gen_schema_files.py. Embedded object type -- has no
// own Sanity document lifecycle; nests inside the document types that
// reference it (see sanity-content-model.md).
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'applicationRequirement',
  title: 'Application Requirement',
  type: 'object',
  fields: [
    defineField({
      name: 'requirement_type',
      title: 'Requirement Type',
      type: 'string',
      options: { list: ["form", "transcript_or_school_report", "recommendation", "essay", "standardized_test_score", "self_reported_record", "interview_or_evaluation_event", "financial_document", "other"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'necessity',
      title: 'Necessity',
      type: 'string',
      options: { list: ["required", "recommended", "optional"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
    }),
    defineField({
      name: 'notes',
      title: 'Notes',
      type: 'text',
    }),
  ],
})
