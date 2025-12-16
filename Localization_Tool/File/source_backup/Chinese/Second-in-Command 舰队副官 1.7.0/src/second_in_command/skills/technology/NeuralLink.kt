package second_in_command.skills.technology

import com.fs.starfarer.api.Global
import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.HullMods
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.NeuralLinkScript
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class NeuralLink : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "配备了 神经接口 船插的舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        val control = Global.getSettings().getControlStringForEnumName(NeuralLinkScript.TRANSFER_CONTROL)
        val desc = Global.getSettings().getControlDescriptionForEnumName(NeuralLinkScript.TRANSFER_CONTROL)

        tooltip.addPara("让两艘舰船能够同时受益于你个人的技能，并且让你可以快速在两舰间切换", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 目标舰船{不能处于}军官 或 AI 核心 操控之下", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "不能处于")

        tooltip.addSpacer(10f)

        tooltip.addPara("舰船插件：{神经接口 - 允许在舰船之间快速切换", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "神经接口")
        tooltip.addPara("舰船插件：{神经集成器 - 自动化舰船专用的神经接口", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "神经集成器")

        tooltip.addSpacer(15f)

        tooltip.addPara("*使用 \"$desc\" 键 [$control] 即可在不同舰船之间进行切换", 0f, Misc.getGrayColor(), Misc.getHighlightColor(), "$control")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {



    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {



    }



    override fun onActivation(data: SCData) {
        var faction = Global.getSector().playerFaction
        if (!faction.knownHullMods.contains(HullMods.NEURAL_INTEGRATOR)) {
            faction.addKnownHullMod(HullMods.NEURAL_INTEGRATOR)
        }
        if (!faction.knownHullMods.contains(HullMods.NEURAL_INTERFACE)) {
            faction.addKnownHullMod(HullMods.NEURAL_INTERFACE)
        }

        Global.getSector().characterData.person.stats.dynamic.getMod(Stats.HAS_NEURAL_LINK).modifyFlat("sc_neural_link", 1f)
    }

    //In case vanilla neural link deactivates it
    override fun advance(data: SCData, amount: Float) {
        Global.getSector().characterData.person.stats.dynamic.getMod(Stats.HAS_NEURAL_LINK).modifyFlat("sc_neural_link", 1f)
    }

    override fun onDeactivation(data: SCData) {
        Global.getSector().characterData.person.stats.dynamic.getMod(Stats.HAS_NEURAL_LINK).unmodify("sc_neural_link")
    }

}