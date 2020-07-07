# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class dossier_import(models.Model):
    _name = 'dossier_import'
    _description = 'Dossier Import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def compute_taux_frais_approche(self):
        for rec in self:
            rec.taux_frais_approche = (rec.total_frais_dh / ((rec.total_frais_dh+rec.total_achats_dh) or 1))*100

    name = fields.Char(u"Number", size=64,readonly=True,default=False,copy=False)
    date_dossier_import=fields.Date(u"Date")
    partner_id =fields.Many2one('res.partner', u'Vendor')
    num_dum= fields.Char(u"DUM N°", size=128)
    date_dum= fields.Date(u"DUM date")
    marchandise= fields.Char(u"Marchandise", size=128)
    country_id=fields.Many2one('res.country', u'Coming from')
    devise_id=fields.Many2one('res.currency', u'Currency')
    taux_change= fields.Float(u'Exchange rates', digits=(16,4))
    poids_brut= fields.Char(u'Gross Weight', size=265)
    nbre_colis= fields.Char(u'Number of packages', size=265)
    num_quittance= fields.Char(u"QUITTANCE number", size=128)
    date_quittance= fields.Date(u"QUITTANCE date")
    fiche_liquidation= fields.Char(u"Liquidation form", size=128)
    company_id = fields.Many2one('res.company', string=u'Company', readonly=True,default=lambda self: self.env['res.company']._company_default_get('dossier_import'))
    #picking_ids = fields.Many2many('stock.picking','rel_di_picking','dossier_id','picking_id',string=u"Réceptions",copy=False)
    purchase_ids = fields.Many2many('purchase.order','rel_di_purchase','dossier_id','purchase_id',string=u"Orders",copy=False)
    line_achat_ids = fields.One2many('achat.line.dossier.import','dossier_id',string=u"Purchasing lines")
    line_frais_ids = fields.One2many('frais.dossier.import','dossier_id',string=u"Fees")
    total_achats_dh = fields.Float(string=u"Total purchases (DH)", compute='get_total_achats',)
    total_frais_dh = fields.Float(string=u"Total fees (DH)", compute='get_total_frais')
    taux_frais_approche = fields.Float(compute='compute_taux_frais_approche',string="Approach fee rates %" ,copy=False)
    tag_ids = fields.Many2many('dossier.import.tags','rel_di_tags','dossier_id','tag_id',string=u"Stages")

    # Ajout de champs de suivi
    num_portnet = fields.Char(string=u"N° Portnet")
    transitaire_id = fields.Many2one('res.partner',string=u"Forwarder")
    transporteur_id = fields.Many2one('res.partner',string=u"Carrier")
    incoterm_id = fields.Many2one('account.incoterms', string=u"Incoterm")
    date_facturation = fields.Date(string=u"Invoice date")
    date_mise_en_transport = fields.Date(string=u"Date of shipment")
    date_arrivee_magasin = fields.Date(string=u"Store Arrival Date")
    date_paiement_fournisseur = fields.Date(string=u"Supplier payment date")

    # Totaux
    tot_qte_cmd = fields.Float(string=u"Total Qty ordered", compute='get_totaux')
    tot_poids = fields.Float(string=u"Total weight", compute='get_totaux')
    tot_volume = fields.Float(string=u"Total volume", compute='get_totaux')

    # Champ de répartition analytique
    product_new_price_ids = fields.One2many('product.new.price','dossier_id',string=u"Cost price")
    analytic_line_ids = fields.One2many('ligne.distrib.analytic','dossier_id',string=u"Analytical breakdown lines")

    state = fields.Selection([('encours', 'In progress'),
                             ('termine', u'Finished'),
                             ('traiter', 'Treated'),
                             ('valide', u'Validated')], u'Status', default='encours' ,readonly=True, required=True)



    def to_termine(self):
        self.write( {'state': 'termine'})
        return True

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('dossier.import')
        return super(dossier_import, self).create(vals)

    @api.onchange('taux_change')
    def onchange_taux_change(self):
        for rec in self:
            for frais in rec.line_frais_ids:
                frais.currency_rate = rec.taux_change

    @api.onchange('purchase_ids')
    def onchange_purchase_ids(self):
        if self.purchase_ids:
            self.partner_id = self.purchase_ids[0].partner_id

    @api.depends('line_achat_ids')
    def get_totaux(self):
        for rec in self:
            count = 0
            somme_qty_cmd = 0
            somme_poids = 0
            somme_volume = 0

            for line in rec.line_achat_ids:
                count += 1
                somme_qty_cmd += line.ordered_qty
                somme_poids += line.product_id.product_tmpl_id.weight * line.ordered_qty
                somme_volume += line.product_id.product_tmpl_id.volume * line.ordered_qty

            rec.tot_qte_cmd = somme_qty_cmd
            rec.tot_poids = somme_poids
            rec.tot_volume = somme_volume

    # Méthode qui calcule le total des achats en DH
    def get_total_achats(self):
        for rec in self:
            somme = 0.0
            for line in rec.line_achat_ids:
                somme+= line.montant_dirham
            rec.total_achats_dh = somme

    # Méthode qui calcule le total des frais en DH
    def get_total_frais(self):
        for rec in self:
            somme = 0.0
            for line in self.line_frais_ids:
                somme+= line.amount_dh
            rec.total_frais_dh = somme

    # Méthode qui affiche tous les articles impliqués dans les bons de commande achat
    # @api.multi
    # def generate_achat_line(self):
    #     for rec in self:
    #         rec.line_achat_ids.unlink()
    #
    #         for commande in rec.purchase_ids:
    #             for line in commande.order_line:
    #                 line_value = {'dossier_id':rec.id,
    #                               'purchase_id':commande.id,
    #                               'product_id':line.product_id.id,
    #                               'ordered_qty': line.product_qty,
    #                               'taux_douane':line.product_id.taux_douane,
    #                               'prix_devise':line.price_unit,
    #                               'montant_devise': line.price_unit * line.product_qty,
    #                              }
    #                 self.env['achat.line.dossier.import'].create(line_value)

    def generate_achat_line(self):
        self.ensure_one()
        return {
            'name': 'Import incoming shipment',
            'res_model': 'landed.cost.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            # 'res_id': self.id,
            # 'view_id': self.env.ref('project_base.view_cancel_invoice_validation_wizard').id,
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    # Méthode qui effectue les répartitions analytiques
    #Droits de douane = taux( %) x (valeur du produit + coût du transport + assurance...)
    def generer_distribution_analytic(self):
        for rec in self:
            rec.analytic_line_ids.unlink()

            for frais in rec.line_frais_ids:
                split = frais.split_method
                for line in rec.line_achat_ids:
                    taux,val_produit=0,0
                    if frais.product_id.is_douane and line.product_id.taux_douane >0 :
                        taux = (line.product_id.taux_douane) / 100
                        val_produit = line.montant_devise * frais.currency_rate * taux
                    elif frais.product_id.is_copyright and line.product_id.copyright >0 :
                        taux = 1/(frais.amount_dh or 1)
                        val_produit = line.product_id.copyright * frais.currency_rate * line.ordered_qty
                    elif split == 'by_quantity':
                        taux = line.ordered_qty / (rec.tot_qte_cmd or 1)
                    elif split == 'by_current_cost_price' and not frais.product_id.is_douane:
                        taux = line.montant_dirham  / (rec.total_achats_dh or 1)
                    elif split == 'by_weight':
                        taux = line.product_id.product_tmpl_id.weight * line.ordered_qty / (rec.tot_poids or 1)
                    elif split == 'by_volume':
                        taux = line.product_id.product_tmpl_id.volume * line.ordered_qty / (rec.tot_volume or 1)
                    elif split == 'equal':
                        taux = 1 * line.ordered_qty / (rec.tot_qte_cmd or 1)
                    distrib_line = {'dossier_id':rec.id,
                                    'frais_id':frais.product_id.id,
                                    'product_id':line.product_id.id,
                                    'montant_unitaire': ((frais.amount_dh * taux)+val_produit)/(line.ordered_qty or 1),
                                    'price_unit_devise':line.prix_devise,
                                    'price_total_devise':line.montant_devise
                                    }
                    self.env['ligne.distrib.analytic'].create(distrib_line)

    def get_couts_unitaires(self):
        couts_unitaires = {}
        for rec in self:
            for line in rec.analytic_line_ids:
                if not line.product_id.id in couts_unitaires.keys():
                    couts_unitaires[line.product_id.id] = {'amount': line.montant_unitaire,
                                                           'prix_achat': 0,
                                                           'quantite': 0,
                                                           'price_unit_devise': line.price_unit_devise,
                                                           'price_total_devise': line.price_total_devise
                                                           }
                else:
                    couts_unitaires[line.product_id.id]['amount'] += line.montant_unitaire
                    # Ressortir le prix d'achat moyen de chaque article
            for article in couts_unitaires.keys():
                        somme_qte = 0
                        somme_montant = 0
                        for line in rec.line_achat_ids.filtered(lambda r: r.product_id.id == article):
                            somme_qte += line.ordered_qty
                            somme_montant += line.montant_dirham
                        couts_unitaires[line.product_id.id]['prix_achat'] = somme_montant / (somme_qte or 1)
                        couts_unitaires[line.product_id.id]['quantite'] = somme_qte
        return couts_unitaires

    #calcul le total des frais douane seulement
    def get_frais_douane(self,article):
        couts_unitaires = self.get_couts_unitaires()
        for rec in self:
               somme=0.0
               for frais in rec.analytic_line_ids:
                   if frais.frais_id.is_douane and article == frais.product_id.id:
                        somme +=frais.montant_unitaire
        return somme

    #calcul le total des Droits d’auteurs seulement
    def get_copyright(self,article):
        for rec in self:
               somme=0.0
               for frais in rec.analytic_line_ids:
                   if frais.frais_id.is_copyright and article == frais.product_id.id:
                        somme +=frais.montant_unitaire
        return somme

    #calcul le total des frais Hors douane
    def get_autres_frais(self, article):
        couts_unitaires = self.get_couts_unitaires()
        for rec in self:
            somme = 0.0
            for frais in rec.analytic_line_ids:
                if not frais.frais_id.is_douane and article == frais.product_id.id:
                    somme += frais.montant_unitaire
        return somme

    # Méthode qui calcul le prix de revient impliqués dans le dossier d'import
    def calcul_cost_price(self):
        total_douane = 0
        total_copyright = 0
        for rec in self:
            for frais in rec.line_frais_ids:
                 if frais.product_id.is_douane or frais.product_id.is_copyright:
                        frais.amount =0
            self.generer_distribution_analytic()
            rec.product_new_price_ids.unlink()
            couts_unitaires=self.get_couts_unitaires()

            for article in couts_unitaires.keys():
                article_tmpl = self.env['product.product'].search([('id','=',article)]).product_tmpl_id
                prix_revient_initial = article_tmpl.standard_price
                stock_initital = article_tmpl.qty_available - couts_unitaires[article]['quantite']

                prix_dossier = couts_unitaires[article]['amount'] + couts_unitaires[article]['prix_achat']

                new_price = prix_dossier

                #Créer la table des articles avec le nouveau prix
                new_price_product = {'dossier_id':rec.id,
                                    'product_id':article,
                                    'price': new_price,
                                    'total_price': new_price * couts_unitaires[article]['quantite'],
                                    'price_unit_devise': couts_unitaires[article]['price_unit_devise'],
                                    'price_total_devise':couts_unitaires[article]['price_total_devise'],
                                    'frais_douane':self.get_frais_douane(article),
                                    'copyright':self.get_copyright(article),
                                    'autres_frais':self.get_autres_frais(article),
                                    'taux':rec.taux_change,
                                    'qty':couts_unitaires[article]['quantite']
                                    }
                rec_new_price=self.env['product.new.price'].create(new_price_product)
                for rec_new in rec_new_price:
                    total_douane += rec_new.frais_douane * rec_new.qty
                    total_copyright += rec_new.copyright * rec_new.qty
            for frais in rec.line_frais_ids:
                if frais.product_id.is_douane:
                    frais.amount_dh = total_douane
                    if frais.currency_id.id != self.company_id.currency_id.id:
                        frais.amount = total_douane/(frais.currency_rate or 1)
                    else:
                        frais.amount = total_douane
                if frais.product_id.is_copyright:
                    frais.amount_dh = total_copyright
                    if frais.currency_id.id != self.company_id.currency_id.id:
                        frais.amount = total_copyright/(frais.currency_rate or 1)
                    else:
                        frais.amount = total_copyright
        return  couts_unitaires

    #  # Effectuer La mise à jour du prix de revient
    # def update_cost_price(self):
    #      couts_unitaires = self.get_couts_unitaires()
    #      for rec in self:
    #         for article in couts_unitaires.keys():
    #             article_tmpl = self.env['product.product'].search([('id','=',article)]).product_tmpl_id
    #             prix_revient_initial = article_tmpl.standard_price
    #             stock_initital = article_tmpl.qty_available - couts_unitaires[article]['quantite']
    #
    #             prix_dossier = couts_unitaires[article]['amount'] + couts_unitaires[article]['prix_achat']
    #             if prix_revient_initial > 0:
    #                 stock_global = stock_initital + couts_unitaires[article]['quantite']
    #                 new_price = ((prix_revient_initial * stock_initital)+(prix_dossier * couts_unitaires[article]['quantite'])) / (stock_global or 1)
    #             else:
    #                 new_price = prix_dossier
    #             article_tmpl.standard_price = new_price


    def update_cost_price(self):
        couts_unitaires = self.get_couts_unitaires()
        for cost in self:
            for line in cost.line_achat_ids.filtered(lambda line: line.move_id):
                product = line.move_id.product_id
                if product.cost_method == 'average' and not float_is_zero(product.quantity_svl,
                                                                          precision_rounding=product.uom_id.rounding):

                    remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                    linked_layer = line.move_id.stock_valuation_layer_ids[-1]

                    cost_to_add = (remaining_qty / line.move_id.product_qty) * couts_unitaires[line.product_id.id]['amount']*couts_unitaires[line.product_id.id]['quantite']
                    if not cost.company_id.currency_id.is_zero(cost_to_add):
                        self.env['stock.valuation.layer'].create({
                            'value': cost_to_add,
                            'unit_cost': 0,
                            'quantity': 0,
                            'remaining_qty': 0,
                            'stock_valuation_layer_id': linked_layer.id,
                            'description': cost.name,
                            'stock_move_id': line.move_id.id,
                            'product_id': line.move_id.product_id.id,
                            'company_id': cost.company_id.id,
                        })

                    product.with_context(force_company=self.company_id.id).sudo().standard_price += cost_to_add / product.quantity_svl

                if product.cost_method == 'standard':
                    new_price = couts_unitaires[line.product_id.id]['amount'] + couts_unitaires[line.product_id.id][
                                                                                      'prix_achat']
                    counterpart_account_id = product.property_account_expense_id.id or product.categ_id.property_account_expense_categ_id.id
                    product._change_standard_price(new_price,
                                                counterpart_account_id=counterpart_account_id)

    def unlink(self):
        if self.state != "encours":
            raise UserError(('Action non valide,Impossible de supprimer un dossier terminer'))
        return super(dossier_import, self).unlink()

    folder_ids = fields.Many2many('stock.move', compute="_compute_move_ids", string="MOVES",store=True)

    @api.depends('line_achat_ids')
    def _compute_move_ids(self):
        for r in self:
            moves = []
            for line in r.line_achat_ids:
                print(line.move_id)
                print(line.move_id)
                print(line.move_id)
                if line.move_id:
                    moves.append(line.move_id.id)
            print("=========",moves)
            r.folder_ids = [(6, 0, moves)]



class AchatLineDossierImport(models.Model):
    _name = 'achat.line.dossier.import'

    dossier_id = fields.Many2one('dossier_import')
    purchase_id = fields.Many2one('purchase.order',string=u"N° BC")
    currency_id = fields.Many2one('res.currency', related='purchase_id.currency_id', string=u"Currency")
    #picking_id = fields.Many2one('stock.picking', string=u"N° Réception")
    product_id = fields.Many2one('product.product',string=u"Product")
    ordered_qty = fields.Float(string=u"Ordered Qty")
    taux_douane=fields.Float(string='Customs rate',readonly=True)
    prix_devise = fields.Float(string=u"Price (Currency)")
    montant_devise = fields.Float(string=u"Amount (Currency)")
    montant_dirham = fields.Float(string=u"Amount (DHS)", compute='get_montant_dh')
    move_id = fields.Many2one('stock.move',string=u"Move")
    import_id = fields.Many2one('dossier_import',string=u"Import id")


    # Méthode qui calcule le montant en DHS relatif au frais inséré

    @api.depends('montant_devise','currency_id','dossier_id.taux_change','dossier_id.company_id')
    def get_montant_dh(self):
        for rec in self:
            company_currency = rec.dossier_id.company_id.currency_id
            if rec.currency_id != company_currency:
                rec.montant_dirham = rec.montant_devise * rec.dossier_id.taux_change
            else:
                rec.montant_dirham = rec.montant_devise

    def unlink(self):
        for r in self:
            print("=========================",r.move_id.folder_id)
            r.move_id.folder_id = False
        return super(AchatLineDossierImport, self).unlink()


class FraisDossierImport(models.Model):
    _name = 'frais.dossier.import'

    def get_split_methods(self):

        return (
            ('by_current_cost_price', 'By current price'),
            ('equal','Equal'),
            ('by_quantity','By quantity'),
            ('by_weight','By weight'),
            ('by_volume','by Volume')
        )

    dossier_id = fields.Many2one('dossier_import')
    product_id = fields.Many2one('product.product',string=u'Fees',domain="[('landed_cost_ok','=',True)]")
    split_method = fields.Selection(string=u"Dispatch mode", selection='get_split_methods',default='by_current_cost_price')
    amount = fields.Float(string=u"Amount")
    currency_id = fields.Many2one('res.currency',string=u"Currency")
    amount_dh = fields.Float(string=u"Amount dhs",compute='get_montant_dh')
    currency_rate = fields.Float(u'Exchage rates', digits=(16,4))

    @api.onchange('product_id')
    def change_split_method(self):
        for rec in self:
            if rec.product_id.split_method:
                rec.split_method = rec.product_id.split_method
                rec.currency_rate = rec.dossier_id.taux_change

    # Méthode qui calcule le montant en DHS relatif au frais inséré
    @api.depends('amount','currency_id','dossier_id.taux_change','dossier_id.company_id')
    def get_montant_dh(self):
        for rec in self:
            if rec.currency_id:
                company_currency = rec.dossier_id.company_id.currency_id
                if rec.currency_id != company_currency:
                    rec.amount_dh = rec.amount * rec.currency_rate
                else:
                    rec.amount_dh = rec.amount
            else:
                rec.amount_dh = 0.0


# Classe qui représente les lignes de distributions analytique des frais du dossier d'import sur chaque article
class LigneDistribAnalytic(models.Model):
    _name = 'ligne.distrib.analytic'
    _order = 'product_id'

    dossier_id = fields.Many2one('dossier_import',string=u"Import Folder")
    frais_id = fields.Many2one('product.product',string=u'Fees')
    product_id = fields.Many2one('product.product',string=u'Product')
    montant_unitaire = fields.Float(string=u"Amount")
    price_unit_devise= fields.Float(string='PU currency')
    price_total_devise= fields.Float(string='Total currency')


class ProductNewPrice(models.Model):
    _name = 'product.new.price'

    def get_prices(self):
        for rec in self:
            rec.price_unite_sale = rec.product_id.lst_price
            prix_vente_ht=rec.price_unite_sale / 1.2
            if prix_vente_ht >0:
              rec.marge=((prix_vente_ht-rec.price)/prix_vente_ht) *100
    product_id = fields.Many2one('product.product',string=u'Product')
    price = fields.Float(string=u"Price Comes Back ")
    total_price = fields.Float(string=u"Total P.Comes Back")
    dossier_id = fields.Many2one('dossier_import',string=u"Import folder")
    qty = fields.Float(string=u'Quantity')
    price_unit_devise = fields.Float(string=u'PU currency')
    price_total_devise = fields.Float(string=u'Total currency')
    frais_douane = fields.Float(string=u'Customs fees DH')
    copyright = fields.Float(string=u'Copyrights DH')
    autres_frais = fields.Float(string=u'Other fees DH')
    taux = fields.Float(string='Rates')
    price_unite_sale=fields.Float(string=u'Selling price incl. VAT', compute='get_prices')
    marge = fields.Float(string=u'margin %', compute='get_prices')


class DossierImportTags(models.Model):
    _name = 'dossier.import.tags'

    name = fields.Char(string="Tag")

class StockMove(models.Model):
    _inherit = 'stock.move'

    folder_id = fields.Many2one('dossier_import', "Dossier")