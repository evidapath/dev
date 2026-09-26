// AUTO-GENERATED from evidapath-schema-v1.2.json ($defs.change_record) by
// 05-sanity/generation/gen_schema_files.py. Regenerate rather than
// hand-editing if the JSON Schema changes -- keeps the two in lockstep.
import { defineType, defineField } from 'sanity'

export default defineType({
  name: 'changeRecord',
  title: 'Change Record',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'Id',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'record_ref',
      title: 'Record',
      type: 'reference',
      weak: true,
      to: [{"type": "country"}, {"type": "city"}, {"type": "university"}, {"type": "campus"}, {"type": "college"}, {"type": "program"}, {"type": "programPathway"}, {"type": "applicantCategory"}, {"type": "admissionStage"}, {"type": "admissionsRequirement"}, {"type": "decisionPlan"}, {"type": "costProfile"}, {"type": "financialRequirement"}, {"type": "scholarship"}, {"type": "financialAidPolicy"}, {"type": "sourceRecord"}, {"type": "derivedCostEstimate"}, {"type": "verificationRecord"}, {"type": "changeRecord"}], // polymorphic: 'EntityType:id' resolved at import time
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'field',
      title: 'Field',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'previous_value',
      title: 'Previous Value',
      type: 'anyValueBox', // untyped-any in JSON Schema -> deterministic value/value_type box, never a stringified value
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'proposed_value',
      title: 'Proposed Value',
      type: 'anyValueBox', // untyped-any in JSON Schema -> deterministic value/value_type box, never a stringified value
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'source_ref',
      title: 'Source',
      type: 'reference',
      weak: true,
      to: [{"type": "country"}, {"type": "city"}, {"type": "university"}, {"type": "campus"}, {"type": "college"}, {"type": "program"}, {"type": "programPathway"}, {"type": "applicantCategory"}, {"type": "admissionStage"}, {"type": "admissionsRequirement"}, {"type": "decisionPlan"}, {"type": "costProfile"}, {"type": "financialRequirement"}, {"type": "scholarship"}, {"type": "financialAidPolicy"}, {"type": "sourceRecord"}, {"type": "derivedCostEstimate"}, {"type": "verificationRecord"}, {"type": "changeRecord"}], // polymorphic: 'EntityType:id' resolved at import time
    }),
    defineField({
      name: 'reason_for_change',
      title: 'Reason For Change',
      type: 'text',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'detected_date',
      title: 'Detected Date',
      type: 'string', // unresolved $ref: iso_date
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'resolution_status',
      title: 'Resolution Status',
      type: 'string',
      options: { list: ["pending", "accepted", "rejected"] },
      validation: (Rule) => Rule.required(),
    }),
  ],
  preview: {
    select: {"a": "field", "b": "resolution_status", "id": "id"},
    prepare: ({a, b, id}) => ({ title: a || id, subtitle: [b, id].filter(Boolean).join(' · ') }),
  },
})
