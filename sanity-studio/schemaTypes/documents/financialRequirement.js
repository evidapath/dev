// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.financial_requirement) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'financialRequirement',
  title: 'Financial Requirement',
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
      weak: true,
      to: [{ type: 'program' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'residency_category_ref',
      title: 'Residency Category',
      type: 'reference',
      weak: true,
      to: [{ type: 'applicantCategory' }],
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'requirement_type',
      title: 'Requirement Type',
      type: 'string',
      options: { list: ["visa_proof_of_funds", "blocked_account", "government_minimum_resources", "enrollment_deposit", "other_liquidity_requirement"] },
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'amount',
      title: 'Amount',
      type: 'number',
    }),
    defineField({
      name: 'currency',
      title: 'Currency',
      type: 'string',
    }),
    defineField({
      name: 'refundable',
      title: 'Refundable',
      type: 'boolean',
    }),
    defineField({
      name: 'frequency',
      title: 'Frequency',
      type: 'string',
    }),
    defineField({
      name: 'administering_body',
      title: 'Administering Body',
      type: 'string',
      validation: (Rule) => Rule.required(),
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
      of: [{ type: 'reference', weak: true, to: [{ type: 'sourceRecord' }] }],
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
    select: {"a": "requirement_type", "currency": "currency", "amount": "amount", "id": "id"},
    prepare: ({a, currency, amount, id}) => ({ title: a || id, subtitle: (amount !== undefined && amount !== null) ? [currency, amount, id].filter(Boolean).join(' · ') : id }),
  },
})
