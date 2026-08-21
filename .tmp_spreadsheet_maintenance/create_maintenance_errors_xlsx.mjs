import fs from "node:fs/promises";
import path from "node:path";

const workspaceDir = path.resolve(".tmp_spreadsheet_maintenance");
const outputDir = path.resolve("outputs/maintenance_erreurs_partie_4_3");
const runtimeNodeModules = "C:\\Users\\Benoit\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\node\\node_modules";
const workspaceNodeModules = path.join(workspaceDir, "node_modules");
await fs.mkdir(workspaceDir, { recursive: true });
try {
  await fs.access(path.join(workspaceDir, "package.json"));
} catch {
  await fs.writeFile(path.join(workspaceDir, "package.json"), JSON.stringify({ private: true, type: "module" }, null, 2));
}
try {
  await fs.lstat(workspaceNodeModules);
} catch {
  await fs.symlink(runtimeNodeModules, workspaceNodeModules, "junction");
}
const { Workbook, SpreadsheetFile } = await import("@oai/artifact-tool");

await fs.mkdir(outputDir, { recursive: true });

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Maintenance erreurs");
sheet.showGridLines = false;

sheet.mergeCells("A1:C1");
sheet.getRange("A1").values = [["4.3. Maintenance — actions à mener en cas d'erreurs"]];
sheet.mergeCells("A2:C2");
sheet.getRange("A2").values = [["Tableau de diagnostic, correction et reprise du parcours"]];

const rows = [
  ["404", "Page ou route API introuvable", "Vérifier l'URL et les routes React/Django, corriger l'appel puis actualiser la page."],
  ["401", "Authentification absente ou expirée", "Se reconnecter et vérifier la validité du jeton JWT et du compte utilisateur."],
  ["403", "Accès interdit", "Vérifier le rôle, les permissions et le rattachement au contrat ou à la ligne concernés."],
  ["400", "Données ou requête invalides", "Lire le détail retourné par l'API, corriger le formulaire, le doublon ou le PDF, puis soumettre à nouveau."],
  ["500", "Erreur interne du serveur", "Consulter le terminal Django et les journaux, corriger la cause, exécuter check/tests puis relancer Django."],
  ["Network Error", "Backend ou frontend inaccessible", "Vérifier les ports 8000 et 3000, relancer le service absent, puis actualiser avec Ctrl+F5."],
  ["PostgreSQL", "Base de données inaccessible", "Vérifier PostgreSQL 16, le port 5433 et les variables POSTGRES_* du fichier .env, puis appliquer les migrations."],
  ["Garnet/Celery", "Tâche non envoyée ou bloquée", "Démarrer Garnet sur 6379 avec --lua, vérifier REDIS_URL, relancer Celery et attendre le message ready."],
  ["PDF manquant", "Aucun fichier associé à la facture", "Vérifier le stockage média et les droits d'écriture, puis réassocier ou réimporter le PDF."],
  ["Notification e-mail", "Envoi SMTP échoué", "Vérifier la configuration SMTP et l'adresse du destinataire sans exposer les secrets, puis renvoyer la notification."],
];

sheet.getRange("A4:C14").values = [["Code ou erreur", "Signification", "Action recommandée"], ...rows];

sheet.mergeCells("A16:C16");
sheet.getRange("A16").values = [["Après correction, reprendre le parcours depuis la dernière étape valide et vérifier le statut avant de republier une facture."]];

// Typographie simple et lisible, proche du tableau de référence.
sheet.getRange("A1:C16").format = {
  font: { name: "Arial", size: 12, color: "#000000" },
  verticalAlignment: "Center",
};
sheet.getRange("A1:C1").format = {
  fill: "#FFFFFF",
  font: { name: "Arial", size: 14, bold: true, color: "#000000" },
  horizontalAlignment: "Center",
  verticalAlignment: "Center",
};
sheet.getRange("A2:C2").format = {
  fill: "#FFFFFF",
  font: { name: "Arial", size: 11, italic: true, color: "#404040" },
  horizontalAlignment: "Center",
  verticalAlignment: "Center",
};
sheet.getRange("A4:C4").format = {
  fill: "#E7E6E6",
  font: { name: "Arial", size: 12, bold: true, color: "#000000" },
  horizontalAlignment: "Center",
  verticalAlignment: "Center",
  wrapText: true,
};
sheet.getRange("A5:A14").format = {
  font: { name: "Arial", size: 12, bold: true, color: "#000000" },
  horizontalAlignment: "Center",
  verticalAlignment: "Top",
  wrapText: true,
};
sheet.getRange("B5:C14").format = {
  font: { name: "Arial", size: 12, color: "#000000" },
  horizontalAlignment: "Left",
  verticalAlignment: "Top",
  wrapText: true,
};
sheet.getRange("A4:C14").format.borders = { preset: "all", style: "thin", color: "#A6A6A6" };
sheet.getRange("A16:C16").format = {
  font: { name: "Arial", size: 11, italic: true, color: "#404040" },
  horizontalAlignment: "Left",
  verticalAlignment: "Center",
  wrapText: true,
};

sheet.getRange("A1:C1").format.rowHeight = 30;
sheet.getRange("A2:C2").format.rowHeight = 24;
sheet.getRange("A4:C4").format.rowHeight = 30;
sheet.getRange("A5:C14").format.rowHeight = 54;
sheet.getRange("A16:C16").format.rowHeight = 34;
sheet.getRange("A:A").format.columnWidth = 22;
sheet.getRange("B:B").format.columnWidth = 40;
sheet.getRange("C:C").format.columnWidth = 82;
sheet.freezePanes.freezeRows(4);

const table = sheet.tables.add("A4:C14", true, "MaintenanceErrors");
table.showFilterButton = true;
table.showBandedColumns = false;

const inspect = await workbook.inspect({
  kind: "table,region",
  sheetId: "Maintenance erreurs",
  range: "A1:C16",
  tableMaxRows: 20,
  tableMaxCols: 3,
  maxChars: 12000,
});
console.log(inspect.ndjson ?? inspect);

const preview = await workbook.render({
  sheetName: "Maintenance erreurs",
  range: "A1:C16",
  scale: 1.5,
  format: "png",
});
await fs.writeFile(path.join(outputDir, "maintenance_erreurs_preview.png"), new Uint8Array(await preview.arrayBuffer()));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(outputDir, "maintenance_erreurs_partie_4_3.xlsx"));
console.log(`Exported: ${path.join(outputDir, "maintenance_erreurs_partie_4_3.xlsx")}`);
