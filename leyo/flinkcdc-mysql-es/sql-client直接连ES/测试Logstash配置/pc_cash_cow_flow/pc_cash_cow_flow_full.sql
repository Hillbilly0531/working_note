SELECT
    tccwf.id,
    DATE_FORMAT(tccwf.create_time, '%Y-%m-%dT%H:%i:%s') as ctime,
    DATE_FORMAT(tccwf.update_time, '%Y-%m-%dT%H:%i:%s') as mtime,
    tccwf.create_user as createUser,
    tccwf.status,
    tccwf.ysb_provider_id as providerId,
    tccwf.ly_product_code as lyProductCode,
    tccwf.prov_drug_code as provDrugCode,
    ifnull(ts.supplier_code, '') as supplierCode,
    CONCAT_WS(':',  tccwf.ysb_provider_id, tccwf.prov_drug_code, tccwf.ly_product_code) as bindProductInfo,
    tccwf.batch_no as batchNo,
    tbdb.owner_id as ownerId,
    tccwf.sales_amount as salesAmount,
    tccwf.batch_p1_price as priceTaxP1,
    tccwf.batch_p0_price as priceTaxP0,
    tccwf.cash_cow_price as cashCowPrice,
    tccwf.profit_amount as profitAmount,
    tccwf.withdraw_profit_sum as withdrawProfitSum,
    tccwf.trade_type as tradeType,
    tccwf.usc_code as uscCode,
    tccwf.sale_order_detail_id as saleDetailId,
    tccwf.supplier_bank_id as supplierBankId,
    tccwf.origin_id as originId,
    tccwf.year_and_month as yearAndMonth,
    tccwf.ysb_bill_code as ysbBillCode,
    tccwf.saleout_no as saleOutNo,
    tccwf.paid_amount as paidAmount,
    tccwf.not_paid_amount as notPaidAmount,
    tccwf.source_type as sourceType,
    DATE_FORMAT(
            case tccwf.source_type
                when 1 then tsod.sales_time
                when 2 then tsod1.sales_time
                when 3 then tsodn.sales_time
                when 8 then tsod8.sales_time
                else null
                end, '%Y-%m-%dT%H:%i:%s') as salesTime,
    if(tpl.label = 1, 1, 0) as isSelectiveProduct,
    tpod.label as isSelectiveBatch
FROM
    db_pay.ts_cash_cow_withdraw_flow tccwf force index (primary)
        INNER JOIN db_admin.ts_provider_auth tpa ON cast(tccwf.ysb_provider_id as char) = tpa.providerId  AND tpa.expiry_date > now()
        LEFT JOIN db_pay.ts_supplier ts ON ts.usc_code = tccwf.usc_code
        LEFT JOIN db_pay.ts_purchased_order_detail tpod ON tpod.ysb_provider_id = tccwf.ysb_provider_id AND tpod.batch_no = tccwf.batch_no AND tpod.io_type = 1
        LEFT JOIN db_data_center.ts_product_label tpl ON tpl.provider_id = tccwf.ysb_provider_id AND tpl.prov_drug_code = tccwf.prov_drug_code
        LEFT JOIN db_biz_dc.ts_bill_detail_balance tbdb ON cast(tccwf.ysb_provider_id as char) = tbdb.company_id AND tccwf.batch_no = tbdb.angle_code_erp AND tbdb.io_type = 1
        LEFT JOIN db_pay.ts_sales_order_detail tsod ON tsod.id = tccwf.sale_order_detail_id and tccwf.source_type = 1
        LEFT JOIN db_biz_dc.ts_sales_order_detail tsod1 ON tsod1.id = tccwf.sale_order_detail_id and tccwf.source_type = 2
        LEFT JOIN db_biz_dc.ts_sales_order_detail_new tsodn ON tsodn.id = tccwf.sale_order_detail_id and tccwf.source_type = 3
        LEFT JOIN db_biz_dc.ts_sales_order_detail_new tsod8 ON tsod8.id = tccwf.sale_order_detail_id and tccwf.source_type = 8
WHERE tccwf.id > :sql_last_value
order by tccwf.id asc
limit 2000