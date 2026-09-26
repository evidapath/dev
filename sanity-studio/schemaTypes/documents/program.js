// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.program) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'program',
  title: 'Program',
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
      weak: true,
      to: [{ type: 'university' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'campus_ref',
      title: 'Campus',
      type: 'reference',
      weak: true,
      to: [{ type: 'campus' }],
    }),
    defineField({
      name: 'program_name',
      title: 'Program Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'faculty_school',
      title: 'Faculty School',
      type: 'string',
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
      name: 'field_of_study',
      title: 'Field Of Study',
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
      name: 'language_of_instruction',
      title: 'Language Of Instruction',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'official_program_url',
      title: 'Official Program Url',
      type: 'url',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'decision_context_academic_year',
      title: 'Decision Context Academic Year',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_refs',
      title: 'Sources',
      type: 'array',
      of: [{ type: 'reference', weak: true, to: [{ type: 'sourceRecord' }] }],
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
      name: 'college_ref',
      title: 'College',
      type: 'reference',
      weak: true,
      to: [{ type: 'college' }],
    }),
    defineField({
      name: 'application_platform',
      title: 'Application Platform',
      type: 'string',
    }),
    defineField({
      name: 'application_requirements',
      title: 'Application Requirements',
      type: 'array',
      of: [{ type: 'applicationRequirement' }],
    }),
    defineField({
      name: 'testing_policy',
      title: 'Testing Policy',
      type: 'testingPolicy',
    }),
  ],
  preview: {
    select: { title: 'program_name', subtitle: 'id' },
  },
})
