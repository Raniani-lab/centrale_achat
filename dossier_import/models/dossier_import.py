# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class dossier_import(models.Model):
    _name = 'dossier_import'
    _description = 'Dossier Import'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def compute_taux_frais_approche(self):
        for rec in self:
            rec.taux_frais_approche = (rec.total_frais_dh / ((rec.total_frais_dh+rec.total_achats_dh) or 1))*100

    name = fields.Char(u"Numéro", size=64,readonly=True,default=False,copy=False)
    date_dossier_import=fields.Date(u"Date")
    partner_id =fields.Many2one('res.partner', u'Fournisseur')
    num_dum= fields.Char(u"DUM N°", size=128)
    date_dum= fields.Date(u"Date DUM")
    marchandise= fields.Char(u"Marchandise", size=128)
    country_id=fields.Many2one('res.country', u'Venant de')
    devise_id=fields.Many2one('res.currency', u'Devise')
    taux_change= fields.Float(u'Taux de change', digits=(16,4))
    poids_brut= fields.Char(u'Poids Brut', size=265)
    nbre_colis= fields.Char(u'Nombre de colis', size=265)
    num_quittance= fields.Char(u"Numéro QUITTANCE", size=128)
    date_quittance= fields.Date(u"Date QUITTANCE")
    fiche_liquidation= fields.Char(u"Fiche de liquidation", size=128)
    company_id = fields.Many2one('res.company', string=u'Société', readonly=True,default=lambda self: self.env['res.company']._company_default_get('dossier_import'))
    #picking_ids = fields.Many2many('stock.picking','rel_di_picking','dossier_id','picking_id',string=u"Réceptions",copy=False)
    purchase_ids = fields.Many2many('purchase.order','rel_di_purchase','dossier_id','purchase_id',string=u"Commandes",copy=False)
    line_achat_ids = fields.One2many('achat.line.dossier.import','dossier_id',string=u"Lignes d'achats")
    line_frais_ids = fields.One2many('frais.dossier.import','dossier_id',string=u"Frais")
    total_achats_dh = fields.Float(string=u"Total achats (DH)", compute='get_total_achats',)
    total_frais_dh = fields.Float(string=u"Total frais (DH)", compute='get_total_frais')
    taux_frais_approche = fields.Float(compute='compute_taux_frais_approche',string="Taux frais d’approche %" ,copy=False)
    tag_ids = fields.Many2many('dossier.import.tags','rel_di_tags','dossier_id','tag_id',string=u"Etapes")

    # Ajout de champs de suivi
    num_portnet = fields.Char(string=u"N° Portnet")
    transitaire_id = fields.Many2one('res.partner',string=u"Transitaire")
    transporteur_id = fields.Many2one('res.partner',string=u"Transporteur")
    incoterm_id = fields.Many2one('account.incoterms', string=u"Incoterm")
    date_facturation = fields.Date(string=u"Date de facturation")
    date_mise_en_transport = fields.Date(string=u"Date de mise en transport")
    date_arrivee_magasin = fields.Date(string=u"Date d'arrivée magasin")
    date_paiement_fournisseur = fields.Date(string=u"Date paiement fournisseur")

    # Totaux
    tot_qte_cmd = fields.Float(string=u"Total Qté commandée", compute='get_totaux')
    tot_poids = fields.Float(string=u"Total poids", compute='get_totaux')
    tot_volume = fields.Float(string=u"Total volume", compute='get_totaux')

    # Champ de répartition analytique
    product_new_price_ids = fields.One2many('product.new.price','dossier_id',string=u"Prix de revient")
    analytic_line_ids = fields.One2many('ligne.distrib.analytic','dossier_id',string=u"Lignes répartitions analytique")

    state = fields.Selection([('encours', 'En cours'),
                             ('termine', u'Terminé'),
                             ('traiter', 'Traité'),
                             ('valide', u'Validé')], u'Statut', default='encours' ,readonly=True, required=True)

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

     # Effectuer La mise à jour du prix de revient
    def update_cost_price(self):
         couts_unitaires = self.get_couts_unitaires()
         for rec in self:
            for article in couts_unitaires.keys():
                article_tmpl = self.env['product.product'].search([('id','=',article)]).product_tmpl_id
                prix_revient_initial = article_tmpl.standard_price
                stock_initital = article_tmpl.qty_available - couts_unitaires[article]['quantite']

                prix_dossier = couts_unitaires[article]['amount'] + couts_unitaires[article]['prix_achat']
                if prix_revient_initial > 0:
                    stock_global = stock_initital + couts_unitaires[article]['quantite']
                    new_price = ((prix_revient_initial * stock_initital)+(prix_dossier * couts_unitaires[article]['quantite'])) / (stock_global or 1)
                else:
                    new_price = prix_dossier
                article_tmpl.standard_price = new_price

    def unlink(self):
        if self.state != "encours":
            raise UserError(('Action non valide,Impossible de supprimer un dossier terminer'))
        return super(dossier_import, self).unlink()


class AchatLineDossierImport(models.Model):
    _name = 'achat.line.dossier.import'

    dossier_id = fields.Many2one('dossier_import')
    purchase_id = fields.Many2one('purchase.order',string=u"N° BC")
    currency_id = fields.Many2one('res.currency', related='purchase_id.currency_id', string=u"Devise")
    #picking_id = fields.Many2one('stock.picking', string=u"N° Réception")
    product_id = fields.Many2one('product.product',string=u"Article")
    ordered_qty = fields.Float(string=u"Qté commandée")
    taux_douane=fields.Float(string='Taux douane',readonly=True)
    prix_devise = fields.Float(string=u"Prix (Devise)")
    montant_devise = fields.Float(string=u"Montant (Devise)")
    montant_dirham = fields.Float(string=u"Montant (DHS)", compute='get_montant_dh')
    move_id = fields.Many2one('stock.move',string=u"Move")

    # Méthode qui calcule le montant en DHS relatif au frais inséré

    @api.depends('montant_devise','currency_id','dossier_id.taux_change','dossier_id.company_id')
    def get_montant_dh(self):
        for rec in self:
            company_currency = rec.dossier_id.company_id.currency_id
            if rec.currency_id != company_currency:
                rec.montant_dirham = rec.montant_devise * rec.dossier_id.taux_change
            else:
                rec.montant_dirham = rec.montant_devise


class FraisDossierImport(models.Model):
    _name = 'frais.dossier.import'

    def get_split_methods(self):

        return (
            ('by_current_cost_price', 'Par prix actuel'),
            ('equal','Egal'),
            ('by_quantity','Par Quantité'),
            ('by_weight','Par Poids'),
            ('by_volume','Par Volume')
        )

    dossier_id = fields.Many2one('dossier_import')
    product_id = fields.Many2one('product.product',string=u'Frais',domain="[('landed_cost_ok','=',True)]")
    split_method = fields.Selection(string=u"Mode répartition", selection='get_split_methods',default='by_current_cost_price')
    amount = fields.Float(string=u"Montant")
    currency_id = fields.Many2one('res.currency',string=u"Devise")
    amount_dh = fields.Float(string=u"Montant dhs",compute='get_montant_dh')
    currency_rate = fields.Float(u'Taux de change', digits=(16,4))

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


# Classe qui représente les lignes de distributions analytique des frais du dossier d'import sur chaque article
class LigneDistribAnalytic(models.Model):
    _name = 'ligne.distrib.analytic'
    _order = 'product_id'

    dossier_id = fields.Many2one('dossier_import',string=u"Dossier import")
    frais_id = fields.Many2one('product.product',string=u'Frais')
    product_id = fields.Many2one('product.product',string=u'Article')
    montant_unitaire = fields.Float(string=u"Montant")
    price_unit_devise= fields.Float(string='PU devise')
    price_total_devise= fields.Float(string='Total devise')


class ProductNewPrice(models.Model):
    _name = 'product.new.price'

    def get_prices(self):
        for rec in self:
            rec.price_unite_sale = rec.product_id.lst_price
            prix_vente_ht=rec.price_unite_sale / 1.2
            if prix_vente_ht >0:
              rec.marge=((prix_vente_ht-rec.price)/prix_vente_ht) *100
    product_id = fields.Many2one('product.product',string=u'Article')
    price = fields.Float(string=u"Prix Revient Un")
    total_price = fields.Float(string=u"Total P.Revient")
    dossier_id = fields.Many2one('dossier_import',string=u"Dossier import")
    qty = fields.Float(string=u'Quantité')
    price_unit_devise = fields.Float(string=u'PU devise')
    price_total_devise = fields.Float(string=u'Total devise')
    frais_douane = fields.Float(string=u'Frais douane DH')
    copyright = fields.Float(string=u'Droits d\'auteurs DH')
    autres_frais = fields.Float(string=u'Autres frais DH')
    taux = fields.Float(string='Taux')
    price_unite_sale=fields.Float(string=u'Prix de vente TTC', compute='get_prices')
    marge = fields.Float(string=u'Marge %', compute='get_prices')


class DossierImportTags(models.Model):
    _name = 'dossier.import.tags'

    name = fields.Char(string="Tag")
