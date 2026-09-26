// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.admissions_requirement) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'admissionsRequirement',
  title: 'Admissions Requirement',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'program_ref',
      title: 'Program',
      type: 'reference',
      to: [{ type: 'program' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'prior_curriculum_category_ref',
      title: 'Prior Curriculum Category',
      type: 'reference',
      to: [{ type: 'applicantCategory' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'curriculum_type',
      title: 'Curriculum Type',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'academic_threshold',
      title: 'Academic Threshold',
      type: 'string',
    }),
    defineField({
      name: 'required_subjects',
      title: 'Required Subjects',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'standardized_tests',
      title: 'Standardized Tests',
      type: 'array',
      of: [{ type: 'testRequirement' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'language_requirements',
      title: 'Language Requirements',
      type: 'array',
      of: [{ type: 'languageRequirement' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'notes',
      title: 'Notes',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'sourceRecord' }] }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'academic_year',
      title: 'Academic Year',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'last_checked',
      title: 'Last Checked',
      type: 'string', // unresolved $ref: iso_date
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'verification_status',
      title: 'Verification Status',
      type: 'string',
      options: { list: ["VERIFIED", "VERIFIED_ABSENT", "SUPPORTED", "ESTIMATED", "UNKNOWN", "CONFLICT"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'record_status',
      title: 'Record Status',
      type: 'string',
      options: { list: ["RESEARCHED", "STRUCTURED", "VERIFIED", "HUMAN_REVIEW", "APPROVED", "PUBLISHED"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'extension_metadata',
      title: 'Extension Metadata',
      type: 'extensionMetadata',
    }),
    defineField({
      name: 'admission_stage_ref',
      title: 'Admission Stage',
      type: 'reference',
      to: [{ type: 'admissionStage' }],
    }),
  ],
  preview: {
    select: {"a": "curriculum_type", "b": "academic_year", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') }),
  },
})
