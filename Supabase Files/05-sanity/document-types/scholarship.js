// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.scholarship) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'scholarship',
  title: 'Scholarship',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'provider',
      title: 'Provider',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'provider_type',
      title: 'Provider Type',
      type: 'string',
      options: { list: ["institutional", "government", "external-private", "university-fund"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'institutions_covered',
      title: 'Institutions Covered',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'programs_covered',
      title: 'Programs Covered',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'degree_levels',
      title: 'Degree Levels',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'eligible_citizenships',
      title: 'Eligible Citizenships',
      type: 'array',
      of: [{ type: 'string' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'residency_restrictions',
      title: 'Residency Restrictions',
      type: 'text',
    }),
    defineField({
      name: 'academic_criteria',
      title: 'Academic Criteria',
      type: 'text',
    }),
    defineField({
      name: 'other_eligibility_criteria',
      title: 'Other Eligibility Criteria',
      type: 'text',
    }),
    defineField({
      name: 'award_type',
      title: 'Award Type',
      type: 'string',
      options: { list: ["full_tuition", "partial_tuition", "fixed_amount", "stipend", "living_cost_support", "fee_waiver", "mixed"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'award_amount',
      title: 'Award Amount',
      type: 'string',
    }),
    defineField({
      name: 'award_amount_currency',
      title: 'Award Amount Currency',
      type: 'string',
    }),
    defineField({
      name: 'renewable',
      title: 'Renewable',
      type: 'boolean',
    }),
    defineField({
      name: 'renewal_conditions',
      title: 'Renewal Conditions',
      type: 'text',
    }),
    defineField({
      name: 'duration',
      title: 'Duration',
      type: 'string',
    }),
    defineField({
      name: 'application_deadline',
      title: 'Application Deadline',
      type: 'string',
    }),
    defineField({
      name: 'deadline_academic_year',
      title: 'Deadline Academic Year',
      type: 'string',
    }),
    defineField({
      name: 'official_source_url',
      title: 'Official Source Url',
      type: 'url',
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
      name: 'college_ref',
      title: 'College',
      type: 'reference',
      to: [{ type: 'college' }],
    }),
  ],
  preview: {
    select: { title: 'name', subtitle: 'id' },
  },
})
