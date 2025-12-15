package second_in_command.skills.automated

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import org.magiclib.subsystems.MagicSubsystemsManager
import second_in_command.SCData
import second_in_command.skills.automated.scripts.FinalGambitActivator
import second_in_command.specs.SCBaseSkillPlugin

class FinalGambit : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有自动化舰船"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("为舰船配备 \"孤注一掷\" 舰船系统。", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("   - 激活该舰船系统将会启动 烈焰驱动器 并且使舰船处于无敌状态", 0f)
        tooltip.addPara("   - 舰船系统的持续时间结束时，舰船将会以比正常情况下更强的力量和范围剧烈爆炸", 0f)
        tooltip.addPara("   - 当舰船的船体结构值低于 20%% 时切换舰船系统", 0f, Misc.getTextColor(), Misc.getHighlightColor(), "20%")

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {
        if (Misc.isAutomated(stats)) {

        }
    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {
        if (Misc.isAutomated(ship)) {
            var activator = FinalGambitActivator(ship!!)
            MagicSubsystemsManager.addSubsystemToShip(ship, activator)
        }
    }


}