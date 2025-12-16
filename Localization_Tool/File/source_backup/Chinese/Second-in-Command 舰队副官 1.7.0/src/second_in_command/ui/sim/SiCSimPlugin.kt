package second_in_command.ui.sim

import com.fs.starfarer.api.GameState
import com.fs.starfarer.api.Global
import com.fs.starfarer.api.fleet.FleetMemberAPI
import com.fs.starfarer.api.impl.SimulatorPluginImpl
import com.fs.starfarer.api.plugins.SimulatorPlugin
import com.fs.starfarer.api.plugins.SimulatorPlugin.SimOptionData
import com.fs.starfarer.api.plugins.SimulatorPlugin.SimOptionSelectorData
import org.lazywizard.lazylib.MathUtils
import second_in_command.SCUtils
import second_in_command.misc.NPCOfficerGenerator
import second_in_command.misc.SCSettings

class SiCSimPlugin : SimulatorPluginImpl() {

    companion object {
        var EXECUTIVE_ID: String = "second_in_command"
        var EXECUTIVE_NONE = "none"
        var EXECUTIVE_LIGHT = "light"
        var EXECUTIVE_MID = "mid"
        var EXECUTIVE_HIGH = "high"
        var EXECUTIVE_MATCH = "match"
    }



    override fun resetToDefaults(withSave: Boolean) {
        super.resetToDefaults(withSave)
        uiStateData.settings.put(EXECUTIVE_ID, EXECUTIVE_NONE)
        if (withSave) {
            saveUIStateData()
        }
    }

    override fun getSimOptions(category: SimulatorPlugin.SimCategoryData?): MutableList<SimulatorPlugin.AdvancedSimOption> {
        var result = super.getSimOptions(category)

        //Dont appear in missions
        if (Global.getCombatEngine()?.isInCampaignSim == true) {
            var data = SCUtils.getPlayerData() ?: return result
            var skills = data.getAllActiveSkillsPlugins().count()

            var text = "执行军官会根据部署的舰船群来分配。只有同时部署的舰队才会共用相同的执行军官。"

            val execs = SimOptionSelectorData(EXECUTIVE_ID, "执行军官", false)
            execs.options.add(SimOptionData(EXECUTIVE_NONE,"无",
                "敌方舰队没有执行军官。",
                "officers_none"))
            execs.options.add(SimOptionData(EXECUTIVE_LIGHT, "低, 5-7 技能",
                "敌方舰队的执行军官总计掌握 5-7 个技能。" +
                        "\n\n$text",
                "officers_some"))
            execs.options.add(SimOptionData(EXECUTIVE_MID,  "中, 11-12 技能",
                "敌方舰队的执行军官总计掌握 11-12 个技能。" +
                        "\n\n$text",
                "officers_all"))
            execs.options.add(SimOptionData(EXECUTIVE_HIGH, "高, 16 技能",
                "敌方舰队的执行军官总计掌握 16 个技能。" +
                        "\n\n$text",
                "officers_high"))
            execs.options.add(SimOptionData(EXECUTIVE_MATCH, "同级, $skills 技能",
                "执行军官的技能总数与你的舰队中的有效技能数量相近。会基于难度设置略有调整。" +
                        "\n\n$text",
                "sim_executive_match"))
            result.add(execs)
        }



        return result
    }

    override fun applySettingsToFleetMembers(members: MutableList<FleetMemberAPI>,
                                             category: SimulatorPlugin.SimCategoryData,
                                             settings: MutableMap<String, String>) {
        super.applySettingsToFleetMembers(members, category, settings)

        var skillsSetting = settings.get(EXECUTIVE_ID)
        if (skillsSetting != null) {

            if (skillsSetting == EXECUTIVE_NONE) return

            var skillCount = 0
            if (skillsSetting == EXECUTIVE_LIGHT) skillCount = 4
            if (skillsSetting == EXECUTIVE_MID) skillCount = 9
            if (skillsSetting == EXECUTIVE_HIGH) skillCount = 13
            if (skillsSetting == EXECUTIVE_MATCH) {
                var data = SCUtils.getPlayerData() ?: return
                var playerSkills = data.getAllActiveSkillsPlugins().count()
                var activeOfficers = data.getActiveOfficers().count()

                //-1 for each active officers origin, otherwise the opponent would get more skills
                skillCount = playerSkills - activeOfficers
                if (SCSettings.difficulty == "Easy") skillCount-2
                if (SCSettings.difficulty == "Normal") skillCount-1
                skillCount = MathUtils.clamp(skillCount, 0, 15)
            }

            if (skillCount > 0) {
                for (member in members) {
                    var data = member.fleetData ?: continue
                    var fleet = data?.fleet ?: continue
                    fleet.memoryWithoutUpdate.set(NPCOfficerGenerator.SKILL_COUNT_OVERWRITE_KEY, skillCount)
                    if (fleet != null) SCUtils.getFleetData(fleet)
                }
            }

        }


    }

}