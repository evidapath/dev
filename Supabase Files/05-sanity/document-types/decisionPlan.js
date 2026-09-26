// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.decision_plan) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'decisionPlan',
  title: 'Decision Plan',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'university_ref',
      title: 'University',
      type: 'reference',
      to: [{ type: 'university' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'program_ref',
      title: 'Program',
      type: 'reference',
      to: [{ type: 'program' }],
    }),
    defineField({
      name: 'plan_type',
      title: 'Plan Type',
      type: 'string',
      options: { list: ["early_decision_1", "early_decision_2", "regular_decision", "rolling", "single_stage", "program_specific_stage"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'application_platform',
      title: 'Application Platform',
      type: 'string',
    }),
    defineField({
      name: 'binding',
      title: 'Binding',
      type: 'boolean',
    }),
    defineField({
      name: 'application_deadline',
      title: 'Application Deadline',
      type: 'string',
    }),
    defineField({
      name: 'decision_release_date',
      title: 'Decision Release Date',
      type: 'string',
    }),
    defineField({
      name: 'academic_year',
      title: 'Academic Year',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'notes',
      title: 'Notes',
      type: 'text',
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'sourceRecord' }] }],
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
  ],
  preview: {
    select: {"a": "plan_type", "b": "academic_year", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') }),
  },
})
