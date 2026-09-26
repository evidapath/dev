// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.financial_aid_policy) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'financialAidPolicy',
  title: 'Financial Aid Policy',
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
      name: 'policy_type',
      title: 'Policy Type',
      type: 'string',
      options: { list: ["need_based", "merit_based", "mixed"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'need_assessment_mechanism',
      title: 'Need Assessment Mechanism',
      type: 'string',
    }),
    defineField({
      name: 'need_aware_or_blind',
      title: 'Need Aware Or Blind',
      type: 'string',
      options: { list: ["need_aware", "need_blind", "unknown"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'eligible_population_notes',
      title: 'Eligible Population Notes',
      type: 'text',
    }),
    defineField({
      name: 'award_basis_description',
      title: 'Award Basis Description',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'max_award_cap_description',
      title: 'Max Award Cap Description',
      type: 'text',
    }),
    defineField({
      name: 'application_requirements',
      title: 'Application Requirements',
      type: 'array',
      of: [{ type: 'applicationRequirement' }],
      validation: (Rule) => Rule.required(),
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
      name: 'application_deadline',
      title: 'Application Deadline',
      type: 'string',
    }),
    defineField({
      name: 'academic_year',
      title: 'Academic Year',
      type: 'string',
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
    select: {"a": "policy_type", "b": "need_aware_or_blind", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') }),
  },
})
