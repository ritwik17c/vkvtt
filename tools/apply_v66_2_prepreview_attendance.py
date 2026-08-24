from pathlib import Path

# 1) My Area identity resolver: include active non-teaching/admin staff without making them timetable teachers.
p=Path('v66-home-cloud.js'); s=p.read_text(encoding='utf-8')
old=""" const teachers=Array.isArray(masterData&&masterData.teachers)?masterData.teachers:[];\n const reps=Array.isArray(masterData&&masterData.temporaryReplacements)?masterData.temporaryReplacements:[];\n const knownCode=c=>teachers.some(t=>String(t.code)===String(c))||reps.some(r=>String(r&&r.tempCode)===String(c));"""
new=""" const teachers=Array.isArray(masterData&&masterData.teachers)?masterData.teachers:[];\n const nonTeaching=Array.isArray(masterData&&masterData.nonTeachingStaff)?masterData.nonTeachingStaff.filter(x=>x&&x.active!==false):[];\n const reps=Array.isArray(masterData&&masterData.temporaryReplacements)?masterData.temporaryReplacements:[];\n const personalStaff=[...teachers,...nonTeaching];\n const knownCode=c=>personalStaff.some(t=>String(t.code)===String(c))||reps.some(r=>String(r&&r.tempCode)===String(c));"""
assert old in s, 'resolver header not found'; s=s.replace(old,new,1)
s=s.replace("const emailMatches=teachers.filter(t=>{","const emailMatches=personalStaff.filter(t=>{",1)
s=s.replace("const exact=teachers.filter(t=>normalizePersonName(t.name)===n);","const exact=personalStaff.filter(t=>normalizePersonName(t.name)===n);",1)
p.write_text(s,encoding='utf-8')

# 2) Attendance admin: add Biometric Import button.
p=Path('admin-attendance.html'); s=p.read_text(encoding='utf-8')
needle="<button onclick=\"location.href='admin-attendance-tests.html?v=66.0'\">🧪 Test / Mock Records</button>"
assert needle in s, 'attendance nav needle not found'
s=s.replace(needle,needle+"<button onclick=\"location.href='admin-biometric-import.html?v=66.2'\">📥 Import Biometric History</button>",1)
p.write_text(s,encoding='utf-8')

# 3) Complete replacement Firestore rules: explicit narrow biometric collections.
p=Path('FIRESTORE_RULES_V66_REPLACE_ALL.txt'); s=p.read_text(encoding='utf-8')
needle="""    // Biometric comparison/correction is stored separately. The original event\n    // snapshot and verifier identity form the verification audit record.\n    match /attendanceVerifications/{eventId} {"""
block="""    // Biometric machine imports remain separate from app/geofence punches.\n    // Attendance managers may import/read batches; only Principal/Admin may undo/delete.\n    match /biometricImports/{batchId} {\n      allow get, list: if isAttendanceManager();\n      allow create: if isAttendanceManager()\n                    && request.resource.data.importedBy == request.auth.uid\n                    && request.resource.data.status == 'active';\n      allow update: if isAdmin();\n      allow delete: if isAdmin();\n    }\n\n    match /biometricRecords/{recordId} {\n      allow get, list: if isAttendanceManager();\n      allow create: if isAttendanceManager()\n                    && request.resource.data.importedBy == request.auth.uid\n                    && request.resource.data.batchId is string;\n      allow update: if false;\n      allow delete: if isAdmin();\n    }\n\n"""
assert needle in s, 'rules insertion needle not found'; s=s.replace(needle,block+needle,1)
p.write_text(s,encoding='utf-8')
