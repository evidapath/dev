// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.admission_stage) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'admissionStage',
  title: 'Admission Stage',
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
      name: 'applicant_category_ref',
      title: 'Applicant Category',
      type: 'reference',
      to: [{ type: 'applicantCategory' }],
    }),
    defineField({
      name: 'stage_type',
      title: 'Stage Type',
      type: 'string',
      options: { list: ["university_entry", "faculty_entry", "admission_category", "qualification_recognition", "preparatory_pathway", "selection_stage", "program_entry", "major_declaration", "progression"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'sequence_order',
      title: 'Sequence Order',
      type: 'number',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'description',
      title: 'Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'criteria',
      title: 'Criteria',
      type: 'array',
      of: [{ type: 'selectionCriterion' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'decision_outcome_options',
      title: 'Decision Outcome Options',
      type: 'array',
      of: [{ type: 'string' }],
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
    select: { title: 'name', subtitle: 'id' },
  },
})
