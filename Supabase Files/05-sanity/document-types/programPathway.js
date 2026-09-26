// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.program_pathway) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'programPathway',
  title: 'Program Pathway',
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
      name: 'pathway_type',
      title: 'Pathway Type',
      type: 'string',
      options: { list: ["primary", "integrated_continuation", "alternate_exit"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'degree_type',
      title: 'Degree Type',
      type: 'string',
      options: { list: ["BA", "BSc", "BEng", "BBA", "MA", "MSc", "MEng", "MBA", "PhD", "other"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'degree_type_local',
      title: 'Degree Type Local',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'duration_value',
      title: 'Duration Value',
      type: 'number',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'duration_unit',
      title: 'Duration Unit',
      type: 'string',
      options: { list: ["years", "months", "semesters"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'progression_requirement',
      title: 'Progression Requirement',
      type: 'progressionRequirement',
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
    select: {"a": "degree_type_local", "b": "pathway_type", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') }),
  },
})
