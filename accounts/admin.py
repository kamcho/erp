from django.contrib import admin
from .models import (FeeStructure, Invoice, Payment, AdmissionFee, AdditionalCharges, 
                     MpesaTransaction, AuxiliaryServiceType, AuxiliaryCharge, AuxiliaryPayment)


admin.site.register(MpesaTransaction)
@admin.register(AdmissionFee)
class AdmissionFeeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'created_at')
    search_fields = ('term__name',)

@admin.register(AdditionalCharges)
class AdditionalChargesAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'created_at')
    filter_horizontal = ('grades',)

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'term', 'school', 'amount', 'created_at')
    list_filter = ('term', 'school')
    search_fields = ('name', 'term__name')
    filter_horizontal = ('grade',)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount', 'created_at')
    list_filter = ('fee_structure__term', )
    search_fields = ('student__first_name', 'student__last_name', 'student__adm_no')
    readonly_fields = ('amount', 'is_billed')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'previous_balance', 'current_balance', 'method', 'reference', 'date_paid')
    list_filter = ('method', 'date_paid')
    search_fields = ('student__first_name', 'student__last_name', 'student__adm_no', 'reference')
    readonly_fields = ('previous_balance', 'current_balance', 'recorded_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AuxiliaryServiceType)
class AuxiliaryServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'amount', 'is_active', 'created_at')
    list_filter = ('school', 'is_active')
    search_fields = ('name',)

@admin.register(AuxiliaryCharge)
class AuxiliaryChargeAdmin(admin.ModelAdmin):
    list_display = ('student', 'service_type', 'amount', 'created_at')
    list_filter = ('service_type',)
    search_fields = ('student__first_name', 'student__last_name', 'student__adm_no')

@admin.register(AuxiliaryPayment)
class AuxiliaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'method', 'reference', 'date_paid', 'recorded_by')
    list_filter = ('method', 'date_paid')
    search_fields = ('student__first_name', 'student__last_name', 'reference')
    readonly_fields = ('previous_balance', 'current_balance')

